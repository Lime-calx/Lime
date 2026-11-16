(function(){
  try {
    var B = window.__BRYTHON__;
    var S = B.builtins.str;
    var orig = S.split;
    S.split = function(self){
      var args = Array.prototype.slice.call(arguments);
      var res = orig.apply(this, args);
      var s = (typeof self === 'string') ? self : (self && typeof self.valueOf === 'function' ? self.valueOf() : null);
      if (typeof s === 'string' && s.trim() === '' && args.length <= 2) {
        var sepGiven = args.length === 2 && typeof args[1] === 'string';
        if (!sepGiven && res && res.length === 1 && res[0] === '') {
          return B.builtins.list.$factory();
        }
      }
      return res;
    };
    window.__splitPatched = true;
  } catch (e) { window.__splitPatched = String(e); }
})();
