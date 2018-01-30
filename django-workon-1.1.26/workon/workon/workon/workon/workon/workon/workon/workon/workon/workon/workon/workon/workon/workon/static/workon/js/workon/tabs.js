(function ($, active, hashActive) {

  active = function(href)
  {
      hashActive(href);
  }

  hashActive = function(hash, trigger)
  {
      var trigger = trigger || $('[data-tabs] [href$="'+hash+'"]');
      if(trigger.length)
      {
          var target = $('[data-tabs-target="'+hash.replace( /^#/, '')+'"]');
          if(!target.length) target = $('[data-tabs-id="'+hash.replace( /^#/, '__')+'"]');
          if(!target.length) target = $(hash.replace( /^#/, '#__' ));
          if(!target.length) target = $(hash);

          if(target.length)
          {
              trigger.parents('[data-tabs]').eq(0).find('.active').removeClass('active');
              target.siblings("[id],[data-tabs-target]").removeClass('active');
              trigger.addClass('active');
              target.addClass('active');
              trigger.trigger('tabs.changed', [ trigger, target ]);

              var parent = target.parents("[data-tabs-target]").eq(0);
              if(parent.length)
              {
                  hashActive('#'+parent.data('tabs-target'));
              }
              return true;
          }
      }
      return false;
  }

  $(document).on('click', '[data-tabs] [href]', function(e, self)
  {
      self = $(this);
      var href = self.attr('href').split('#', 2);
      if(href.length == 2)
      {
          var hash = '#'+href[1];
          window.location.replace(('' + window.location).split('#')[0] + hash);
          return !hashActive(hash, self);
          //document.location.hash = hash;
      }
  })
  $(document).ready(function()
  {
      var hash = document.location.hash;
      if(hash) {
          hashActive(hash);
      }
  });
}( jQuery ));
