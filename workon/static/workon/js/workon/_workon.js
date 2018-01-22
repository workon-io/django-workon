

isArray = function(obj) {
    return typeof(obj) == "object" && Object.prototype.toString.call( obj ) === '[object Array]'
}
isDict = function(obj) {
    return typeof(obj) == "object" && Object.prototype.toString.call( obj ) !== '[object Array]'
}