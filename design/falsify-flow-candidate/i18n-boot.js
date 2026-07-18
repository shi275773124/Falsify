/* i18n boot: arm the anti-FOUC guard before first paint. Tiny, dependency-free, runs in <head>. */
try{var l=new URLSearchParams(location.search).get("lang")||localStorage.getItem("falsify-flow-language");if(l==="zh"||l==="zh-CN"){var d=document.documentElement;d.setAttribute("data-i18n-pending","");d.lang="zh-CN"}}catch(e){}
