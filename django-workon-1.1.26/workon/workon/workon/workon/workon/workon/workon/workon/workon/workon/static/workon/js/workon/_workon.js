

function isArray(obj) {
    return typeof(obj) == "object" && Object.prototype.toString.call( obj ) === '[object Array]'
}
function isDict(obj) {
    return typeof(obj) == "object" && Object.prototype.toString.call( obj ) !== '[object Array]'
}