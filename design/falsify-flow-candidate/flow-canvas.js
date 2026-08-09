(() => {
  "use strict";
  const canvas = document.getElementById("flow-canvas");
  if (!canvas) return;

  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const mobile = matchMedia("(max-width: 820px), (hover: none), (pointer: coarse)");
  const hero = canvas.closest(".hero");
  const pointer = { x: 0.72, y: 0.3, tx: 0.72, ty: 0.3, vx: 0, vy: 0 };
  let gl = null, program = null, raf = 0, observer = null;
  let visible = true, running = false, lost = false, width = 1, height = 1;
  let scrollTarget = 0, scrollPhase = 0, quality = 1, slowFrames = 0, frameCount = 0, last = 0;
  const started = performance.now();

  const vertex = `#version 300 es
    in vec2 a_position;
    void main(){ gl_Position = vec4(a_position, 0.0, 1.0); }
  `;

  const fragment = `#version 300 es
    precision highp float;
    uniform vec2 u_resolution;
    uniform vec2 u_pointer;
    uniform float u_time;
    uniform float u_scroll;
    out vec4 outColor;

    float hash(vec2 p){
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }
    float noise(vec2 p){
      vec2 i=floor(p), f=fract(p);
      f=f*f*(3.0-2.0*f);
      return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1)),f.x),f.y);
    }
    float fbm(vec2 p){
      float v=0.0, a=.52;
      mat2 r=mat2(.82,-.57,.57,.82);
      for(int i=0;i<5;i++){ v+=a*noise(p); p=r*p*2.03+vec2(7.1,3.7); a*=.5; }
      return v;
    }
    float ridge(float x, float width){ return exp(-width*abs(x)); }

    void main(){
      vec2 uv=gl_FragCoord.xy/u_resolution.xy;
      vec2 p=(gl_FragCoord.xy*2.0-u_resolution.xy)/u_resolution.y;
      float t=u_time;

      // Two independently advected fields create volume instead of drifting blobs.
      vec2 q=vec2(fbm(p*1.12+vec2(t*.045,-t*.032)),fbm(p*1.08+vec2(-t*.028,t*.041)+8.7));
      vec2 flow=vec2(q.y-q.x, q.x+q.y-1.0);
      vec2 warped=p+flow*.58+vec2(u_scroll*.09,-u_scroll*.16);
      float broad=fbm(warped*1.3+vec2(t*.035,-t*.02));
      float detail=fbm(warped*3.1-flow*.8-vec2(t*.08,t*.035));

      // Refractive-looking caustic ridges: interference contours in warped coordinates.
      float waveA=sin((warped.x*2.3+warped.y*.72+broad*2.8-t*.27)*6.2831);
      float waveB=sin((warped.y*2.05-warped.x*.48+detail*2.2+t*.19)*6.2831);
      float caustic=ridge(waveA+waveB*.62,7.5);
      float fine=ridge(sin((warped.x-warped.y*.55+detail)*31.0+t*.42),10.0);
      caustic=pow(clamp(caustic*.92+fine*.32,0.0,1.0),1.35);

      // Pointer bends the current; influence is supplied by a critically damped spring.
      vec2 mp=(u_pointer*2.0-1.0)*vec2(u_resolution.x/u_resolution.y,1.0);
      mp.y=-mp.y;
      float md=length(p-mp);
      float lens=exp(-md*md*2.8);
      float ring=exp(-28.0*abs(md-(.25+.035*sin(t*.7))));
      caustic+=ring*lens*.42;
      broad+=lens*.15;

      float depth=smoothstep(-1.05,.78,p.y);
      float side=smoothstep(1.55,.05,abs(p.x-.28));
      vec3 deep=vec3(.004,.025,.067);
      vec3 mid=vec3(.015,.19,.43);
      vec3 blue=vec3(.055,.44,.82);
      vec3 aqua=vec3(.20,.87,1.0);
      vec3 col=mix(deep,mid,smoothstep(.17,.78,broad+depth*.12));
      col=mix(col,blue,smoothstep(.52,.9,detail+broad*.24)*.66);
      col+=aqua*caustic*(.22+.64*depth)*side;
      col+=vec3(.08,.42,.66)*pow(max(0.0,1.0-abs(broad-.54)*4.0),3.0)*.2;
      col*=.62+.38*smoothstep(-.95,.65,p.y);
      col*=1.0-.43*smoothstep(.35,1.38,length(p*vec2(.72,.88)));
      col=mix(col,deep,.12*smoothstep(.45,1.0,uv.x));
      outColor=vec4(pow(max(col,0.0),vec3(.88)),1.0);
    }
  `;

  function compile(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source); gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader) || "shader compile failed");
    return shader;
  }

  function initGL() {
    gl = canvas.getContext("webgl2", { alpha:false, antialias:false, depth:false, stencil:false, powerPreference:"high-performance" });
    if (!gl) return false;
    const vs=compile(gl.VERTEX_SHADER,vertex), fs=compile(gl.FRAGMENT_SHADER,fragment);
    program=gl.createProgram(); gl.attachShader(program,vs); gl.attachShader(program,fs); gl.linkProgram(program);
    if (!gl.getProgramParameter(program,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || "shader link failed");
    gl.useProgram(program);
    const buffer=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
    const pos=gl.getAttribLocation(program,"a_position"); gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
    return true;
  }

  const uniforms = () => ({
    resolution: gl.getUniformLocation(program,"u_resolution"), pointer: gl.getUniformLocation(program,"u_pointer"),
    time: gl.getUniformLocation(program,"u_time"), scroll: gl.getUniformLocation(program,"u_scroll")
  });
  let u = null;

  function resize(){
    const rect=canvas.getBoundingClientRect();
    const cap=mobile.matches?1.25:1.5;
    const dpr=Math.min(devicePixelRatio||1,cap)*quality;
    width=Math.max(1,Math.round(rect.width*dpr)); height=Math.max(1,Math.round(rect.height*dpr));
    if(canvas.width!==width||canvas.height!==height){ canvas.width=width; canvas.height=height; }
    if(gl) gl.viewport(0,0,width,height);
  }

  function render(now){
    if(!running||lost||!gl) return;
    const dt=Math.min((now-last)||16.7,50); last=now;
    const stiffness=.00018, damping=.024;
    pointer.vx+=(pointer.tx-pointer.x)*stiffness*dt; pointer.vy+=(pointer.ty-pointer.y)*stiffness*dt;
    pointer.vx*=Math.exp(-damping*dt); pointer.vy*=Math.exp(-damping*dt);
    pointer.x+=pointer.vx*dt; pointer.y+=pointer.vy*dt;
    scrollPhase+=(scrollTarget-scrollPhase)*(1-Math.exp(-dt*.004));
    gl.uniform2f(u.resolution,width,height); gl.uniform2f(u.pointer,pointer.x,1-pointer.y);
    gl.uniform1f(u.time,(now-started)*.001); gl.uniform1f(u.scroll,scrollPhase);
    gl.drawArrays(gl.TRIANGLES,0,3);

    frameCount++;
    if(frameCount%90===0){
      const frameMs=(now-(lastQualityCheck||now))/90; lastQualityCheck=now;
      if(frameMs>23) slowFrames++; else slowFrames=Math.max(0,slowFrames-1);
      if(slowFrames>=2&&quality>.72){ quality=.72; slowFrames=0; resize(); }
    }
    raf=requestAnimationFrame(render);
  }
  let lastQualityCheck=0;

  function drawStatic(){
    if(!gl||lost) return;
    gl.uniform2f(u.resolution,width,height); gl.uniform2f(u.pointer,.72,.70);
    gl.uniform1f(u.time,4.25); gl.uniform1f(u.scroll,scrollPhase); gl.drawArrays(gl.TRIANGLES,0,3);
  }
  function sync(){
    running=visible&&!document.hidden&&!reduceMotion.matches&&!lost;
    cancelAnimationFrame(raf);
    if(running){ last=performance.now(); raf=requestAnimationFrame(render); } else drawStatic();
  }
  function onScroll(){
    if(!hero) return;
    const rect=hero.getBoundingClientRect();
    scrollTarget=Math.max(-1,Math.min(1,-rect.top/Math.max(rect.height,1)));
  }
  function fallback(){
    lost=true; running=false; cancelAnimationFrame(raf); canvas.classList.add("flow-fallback");
  }

  try { if(!initGL()) return fallback(); u=uniforms(); resize(); }
  catch(error){ console.warn("Falsify fluid renderer unavailable; using static fallback.",error); return fallback(); }

  canvas.addEventListener("webglcontextlost",e=>{e.preventDefault();fallback();});
  canvas.addEventListener("webglcontextrestored",()=>location.reload());
  observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;sync();},{threshold:.02}); observer.observe(canvas);
  document.addEventListener("visibilitychange",sync);
  let resizePending=false,lastHeight=canvas.getBoundingClientRect().height;
  addEventListener("resize",()=>{
    if(resizePending) return;
    resizePending=true;
    requestAnimationFrame(()=>{
      resizePending=false;
      const rect=canvas.getBoundingClientRect();
      if(Math.abs(rect.height-lastHeight)<150) return;
      lastHeight=rect.height;
      resize();drawStatic();
    });
  },{passive:true});
  addEventListener("scroll",onScroll,{passive:true}); if(reduceMotion.addEventListener) reduceMotion.addEventListener("change",sync); else reduceMotion.addListener(sync); if(mobile.addEventListener) mobile.addEventListener("change",()=>{resize();sync();}); else mobile.addListener(()=>{resize();sync();});
  if(!mobile.matches) addEventListener("pointermove",e=>{pointer.tx=e.clientX/innerWidth;pointer.ty=e.clientY/innerHeight;},{passive:true});
  onScroll(); sync();
  window.FalsifyFluidField={
    get state(){return{renderer:gl?"webgl2":"fallback",running,visible,reducedMotion:reduceMotion.matches,dprCap:mobile.matches?1.25:1.5,quality,canvas:[width,height]};},
    destroy(){running=false;cancelAnimationFrame(raf);observer?.disconnect();}
  };
})();

