/* スマホのハンバーガーメニュー：ヘッダー右の三本線から横にメニューを出す */
(function(){
  var header = document.querySelector(".site-header .wrap");
  if(!header) return;
  var logo = header.querySelector(".logo");
  var base = (logo && logo.getAttribute("href") || "index.html").replace(/index\.html$/, "");
  var items = [
    ["index.html", "ホーム"],
    ["shindan-ichiran.html", "診断一覧"],
    ["shindan-ichiran.html#tools", "受験ツール"],
    ["kyoutsuu-countdown.html", "共通テストまであと何日？"],
    ["articles/index.html", "記事一覧"],
    ["biboroku/index.html", "京大生の備忘録"],
    ["articles/index.html#search", "記事を検索"],
    ["contact.html", "お問い合わせ"]
  ];
  var btn = document.createElement("button");
  btn.className = "nav-toggle"; btn.type = "button";
  btn.setAttribute("aria-label", "メニューを開く"); btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-controls", "nav-drawer");
  btn.innerHTML = "<span></span><span></span><span></span>";
  header.appendChild(btn);
  var scrim = document.createElement("div"); scrim.className = "nav-scrim";
  var drawer = document.createElement("nav"); drawer.className = "nav-drawer"; drawer.id = "nav-drawer"; drawer.setAttribute("aria-label", "メニュー");
  drawer.innerHTML = '<button type="button" class="nav-close" aria-label="メニューを閉じる">×</button>' +
    items.map(function(x){ return '<a href="' + base + x[0] + '">' + x[1] + '</a>'; }).join("");
  document.body.appendChild(scrim); document.body.appendChild(drawer);
  function set(open){
    document.body.classList.toggle("nav-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if(open) drawer.querySelector("a").focus(); else btn.focus({preventScroll:true});
  }
  btn.addEventListener("click", function(){ set(true); });
  scrim.addEventListener("click", function(){ set(false); });
  drawer.querySelector(".nav-close").addEventListener("click", function(){ set(false); });
  drawer.addEventListener("click", function(e){ if(e.target.tagName === "A") document.body.classList.remove("nav-open"); });
  document.addEventListener("keydown", function(e){ if(e.key === "Escape" && document.body.classList.contains("nav-open")) set(false); });
})();
