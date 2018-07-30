
var Notification = window.Notification || window.mozNotification || window.webkitNotification;



function RedisWebSocket(options, $)
{
    'use strict';
    var opts, ws, deferred, timer, attempts = 1;
    var heartbeat_interval = null, missed_heartbeats = 0;

    if (this === undefined)
        return new RedisWebSocket(options, $);
    if (options.uri === undefined)
        throw new Error('No Websocket URI in options');
    if ($ === undefined)
        $ = jQuery;
    opts = $.extend({ heartbeat_msg: null }, options);
    connect(opts.uri);

    function connect(uri) {
        try {
            if(window.FLOW_DEBUG)
            {
                console.log("Connecting to " + uri + " ...");
            }
            deferred = $.Deferred();
            ws = new WebSocket(uri);
            ws.onopen = on_open;
            ws.onmessage = on_message;
            ws.onerror = on_error;
            ws.onclose = on_close;
            timer = null;
        } catch (err) {
            deferred.reject(new Error(err));
        }
    }

    function send_heartbeat() {
        try {
            missed_heartbeats++;
            if (missed_heartbeats > 3)
                throw new Error("Too many missed heartbeats.");
            ws.send(opts.heartbeat_msg);
        } catch(e) {
            clearInterval(heartbeat_interval);
            heartbeat_interval = null;
            if(window.FLOW_DEBUG)
            {
                console.warn("Closing connection. Reason: " + e.message);
            }
            ws.close();
        }
    }

    function on_open() {
        if(window.FLOW_DEBUG)
        {
            console.log('Connected!');
        }
        // new connection, reset attemps counter
        attempts = 1;
        deferred.resolve();
        if (opts.heartbeat_msg && heartbeat_interval === null) {
            missed_heartbeats = 0;
            heartbeat_interval = setInterval(send_heartbeat, 5000);
        }
        opts.on_open()
    }

    function on_close(evt) {
        if(window.FLOW_DEBUG)
        {
            console.log("Connection closed!");
        }
        if (!timer) {
            // try to reconnect
            var interval = generateInteval(attempts);
            timer = setTimeout(function() {
                attempts++;
                connect(ws.url);
            }, interval);
        }
    }

    function on_error(evt) {
        if(window.FLOW_DEBUG)
        {
            console.error("Websocket connection is broken!");
        }
        deferred.reject(new Error(evt));
    }

    function on_message(evt) {
        if (opts.heartbeat_msg && evt.data === opts.heartbeat_msg) {
            // reset the counter for missed heartbeats
            missed_heartbeats = 0;
        } else if (typeof opts.receive_message === 'function') {
            return opts.receive_message(evt.data);
        }
    }
    function generateInteval (k) {
        var maxInterval = (Math.pow(2, k) - 1) * 1000;

        // If the generated interval is more than 30 seconds, truncate it down to 30 seconds.
        if (maxInterval > 30*1000) {
            maxInterval = 30*1000;
        }

        // generate the interval to a random number between 0 and the maxInterval determined from above
        return Math.random() * maxInterval;
    }

    this.send_message = function(message) {
        ws.send(message);
    };
}


var flow =
{
    _ready: false,
    _loaded: false,
    _connected: false,
    _focus: false,
    _listeners: {},
    AUTO_CONNECT: window.FLOW_AUTO_CONNECT,
    DEBUG: window.FLOW_DEBUG,
    DISCONNECTED_ENABLED: window.FLOW_DISCONNECTED_ENABLED,
    DISCONNECTED_RECEIVE_URL: window.FLOW_DISCONNECTED_RECEIVE_URL,
    DISCONNECTED_SEND_URL: window.FLOW_DISCONNECTED_SEND_URL,
    WS_ENABLED: window.FLOW_WS_ENABLED,
    WS_URI: window.FLOW_WS_URI,
    WS_HEARTBEAT: window.FLOW_WS_HEARTBEAT,
    _redis_ws: null,
    _builtin_notification: window.Notification || window.mozNotification || window.webkitNotification,


    authorizeNotification: function()
    {
        Notification.requestPermission(function (permission) {
            // console.log(permission);
        });
    },

    init: function(source)
    {
        if(flow.DEBUG)
        {
            console.log('%c FLOW initialisation', 'color: #222', source);
        }
        if(!flow._ready)
        {
            flow._ready = true;
            flow._dispatch('flow_ready');

            if(source)
            {
                $.get(source, null, function(wsdata)
                {
                    if(flow.DEBUG)
                    {
                        console.log('%c INITIAL ', 'background: #B1D3D4; color: #222', wsdata);
                    }
                    for( var i in wsdata)
                    {
                        var data = wsdata[i];
                        flow._dispatch(data.type, data.data);
                    }
                    flow._loaded = true;
                    flow._dispatch('flow_loaded');
                    if(flow.AUTO_CONNECT)
                    {
                        flow._connect();
                    }
                });
            }
            else
            {
                flow._loaded = true;
                flow._dispatch('flow_loaded');
                flow._dispatch('flow_no_inital');
                if(flow.AUTO_CONNECT)
                {
                    flow._connect();
                }
                if(flow.DEBUG)
                {
                    console.log('%c FLOW has no INITIAL_URL', 'color: #550000');
                }
                return;
            }


        }
    },
    load: function(source, callback)
    {
        if(!source)
        {
             callback(source)

        }
        else
        {
            if(typeof source == "array" || (typeof source[0] == "object" && source[0].type))
            {

                for( var i in source)
                {
                    flow._dispatch(source[i].type, source[i].data);
                }
                if(callback)
                {
                    callback(source)
                }
            }
            else if(typeof source == "object")
            {
               flow._dispatch(source.type, source.data);
               if(callback)
               {
                    callback(source)
               }

            }
            else if(typeof source == "string")
            {
                $.get(source, null, function(wsdata)
                {
                    //console.log(wsdata)
                    for( var i in wsdata)
                    {
                        var data = wsdata[i]
                        if(self.DEBUG)
                        {
                            console.log('%c RECEIVE ', 'background: #bada55; color: #222', data);
                        }
                        flow._dispatch(data.type, data.data);
                    }
                    if(callback)
                    {
                        callback(source)
                    }
                });
            }
        }
    },
    connect: function()
    {
        if(!flow._redis_ws)
        {
            flow._connect();
        }
    },
    _connect: function()
    {
        if(!flow._redis_ws)
        {
            if(flow.WS_ENABLED && flow.WS_URI)
            {
                flow = this;
                flow._redis_ws = RedisWebSocket(
                {
                    uri: flow.WS_URI+'flow?subscribe-user&publish-user&echo',
                    receive_message: flow._receive,
                    heartbeat_msg: flow.WS_HEARTBEAT,
                    on_open: function()
                    {
                        setTimeout(function()
                        {
                            flow._connected = true;
                            flow._dispatch('flow_connected');
                        }, 500);
                    },
                    flow: flow,
                });
            }
            else
            {
                flow._redis_ws = true; // fake
                flow._dispatch('flow_ws_disabled');
                if(flow.DEBUG)
                {
                    console.log('%c FLOW websocket is disabled ', 'color: #550000');
                }
                if(flow.DISCONNECTED_ENABLED)
                {
                    flow._disconnected_receive(2000);
                }
                else
                {
                    if(flow.DEBUG)
                    {
                        console.log('%c FLOW disconnected is disabled ', 'color: #550000');
                    }
                }
            }
        }

    },
    on: function(type, fct)
    {
        var types = type.split(',')
        for(var i in types)
        {
            var type = $.trim(types[i]);
            listeners = flow._listeners[type];
            if(!listeners) {
                flow._listeners[type] = listeners = [];
            }
            listeners.push(fct);
        }
    },
    _disconnected_send: function(msg)
    {
        if(flow.DISCONNECTED_ENABLED && flow.DISCONNECTED_SEND_URL)
        {
            $.get(flow.DISCONNECTED_SEND_URL, {msg:msg}, function(wsdata)
            {
                for(var i in wsdata)
                {
                    flow._receive(wsdata[i]);
                }
            });
        }
    },
    send: function(type, data)
    {
        var typed_data = {}
        typed_data.type = type;
        typed_data.from = "js"
        typed_data.data = data
        var msg = JSON.stringify(typed_data);
        if(flow._connected && flow._redis_ws)
        {
            if(flow.DEBUG)
            {
                console.log('%c SEND ', 'background: #222; color: #bada55', typed_data);
            }
            flow._redis_ws.send_message(msg);
        }
        else
        {
            flow._disconnected_send(msg);
        }
    },
    _disconnected_receive_timeout: null,
    _disconnected_receive: function(timeout)
    {
        if(flow.DISCONNECTED_ENABLED && flow.DISCONNECTED_RECEIVE_URL)
        {
            if(flow._disconnected_receive_timeout)
            {
                clearTimeout(flow._disconnected_receive_timeout);
            }
            flow._disconnected_receive_timeout = setTimeout(function()
            {
                if(flow.is_active())
                {
                    $.get(flow.DISCONNECTED_RECEIVE_URL, null, function(wsdata)
                    {
                        for(var i in wsdata)
                        {
                            flow._receive(wsdata[i]);
                        }
                    });
                    flow._disconnected_receive(flow.is_focused() ? 5000 : 20000);
                }
            }, timeout);
        }
    },
    _receive: function(msg)
    {
        var data = JSON.parse(msg);
        if(data && data.from != "js")
        {
            if(flow.DEBUG)
            {
                console.log('%c RECEIVE ', 'background: #bada55; color: #222', data);
            }
            flow._dispatch(data.type, data.data);
        }
    },

    _dispatch: function(type, data)
    {
        if(flow._listeners[type])
        {
            for(var i in flow._listeners[type])
            {
                flow._listeners[type][i](data)
                //console.log('LISTEN', json.type, json)
            }
        }
        else
        {
            // console.error('LISTEN', type+" has no listeners.", data)
        }
    },

    trigger: function(type, data)
    {
        flow._dispatch(type, data);
    },

    template: function(id, data)
    {
        if(window.Handlebars && window.Handlebars != "undefined") {

            var source   = $('#'+id).html();
            var template = window.Handlebars.compile(source);
            var html    = template(data);
            return $(html);
        }
        else {
            return $(id);
        }
    },
}



flow = $.extend(flow,
{
    ACTIVITY_DELAY: window.FLOW_ACTIVITY_DELAY, // in MS
    _activity_interval: null,
    _active: true,
    set_active: function(active)
    {
        //console.log('change _active', active)
        if(active != this._active)
        {
            if(active == true) {

                clearTimeout(flow._activity_interval);
                flow._activity_interval = setTimeout(function() { flow.set_active(false); }, flow.ACTIVITY_DELAY);
            }
            this._active = active;
            this._dispatch('activity_changed', active);
        }
    },
    is_active: function(active)
    {
        return this._active;
    },
    _focused: false,
    set_focused: function(focused)
    {
        if(focused != this._focused)
        {
            this._focused = focused;
            this._dispatch('focus_changed', focused);
        }
    },
    is_focused: function(focused)
    {
        return this._focused;
    },
});

flow.on('activity_changed', function()
{
    if(flow.is_active())
    {
        flow._disconnected_receive();
    }
});

flow.on('flow_connected', function(delay)
{
    flow.set_focused(true);

    $(window).mousemove(function() { flow.set_active(true); });
    flow._activity_interval = setTimeout(function() { console.log('first timeout', flow._active); flow.set_active(false); }, flow.ACTIVITY_DELAY);
    $(window).focus(function()
    {
        flow.set_focused(true);
        flow._disconnected_receive(100);
    }).blur(function()
    {
        flow.set_focused(false);
    });
});




window.flow = flow;



