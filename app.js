/* App logic: fetch images from /images via GitHub API; render Featured + Gallery; provide Lightbox */
(() => {
  const featuredCount = 8; // 調整首頁精選張數
  let images = [];
  let currentIndex = -1;

  const featuredEl = document.getElementById('featuredGrid');
  const galleryEl  = document.getElementById('galleryGrid');
  const emptyEl    = document.getElementById('empty');

  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  const lbCap = document.getElementById('lightboxCap');
  const btnClose = document.querySelector('.lightbox-close');
  const btnPrev = document.querySelector('.lightbox .prev');
  const btnNext = document.querySelector('.lightbox .next');

  const colControl = document.getElementById('colControl');
  const shuffleBtn = document.getElementById('shuffleBtn');

  function inferRepoInfo() {
    const host = window.location.hostname;  // e.g., username.github.io
    const path = window.location.pathname.replace(/^\//, ''); // e.g., repo/ or "" for root
    const owner = host.split('.')[0];
    let repo = '';
    if (!path || path.split('/')[0] === '') {
      repo = `${owner}.github.io`;
    } else {
      repo = path.split('/')[0];
    }
    return { owner, repo };
  }

  async function getDefaultBranch(owner, repo) {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`);
    if (!res.ok) throw new Error('無法取得 Repository 資訊：' + res.status);
    const data = await res.json();
    return data.default_branch || 'main';
  }

  async function listImages(owner, repo, branch, dir = 'images') {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(dir)}?ref=${encodeURIComponent(branch)}`);
    if (res.status === 404) return [];
    if (!res.ok) throw new Error('讀取 /images 失敗：' + res.status);
    const items = await res.json();
    const exts = new Set(['.jpg','.jpeg','.png','.gif','.webp','.avif','.JPG','.JPEG','.PNG','.GIF','.WEBP','.AVIF']);
    return items
      .filter(it => it.type === 'file' && [...exts].some(ext => it.name.endsWith(ext)))
      .map(it => ({
        name: it.name,
        raw_url: `https://raw.githubusercontent.com/${owner}/${repo}/${encodeURIComponent(branch)}/images/${encodeURIComponent(it.name)}`
      }));
  }

  function filenameToAlt(name) {
    return name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
  }

  function makeCard(img, index) {
    const fig = document.createElement('figure');
    fig.className = 'card';
    const image = document.createElement('img');
    image.loading = 'lazy';
    image.decoding = 'async';
    image.src = img.raw_url;
    image.alt = filenameToAlt(img.name);
    image.addEventListener('click', () => openLightbox(index));

    const cap = document.createElement('figcaption');
    cap.textContent = img.name;

    fig.appendChild(image);
    fig.appendChild(cap);
    return fig;
  }

  function render() {
    featuredEl.innerHTML = '';
    galleryEl.innerHTML = '';

    const featured = images.slice(0, featuredCount);
    const rest = images.slice(featuredCount);

    featured.forEach((img, i) => featuredEl.appendChild(makeCard(img, i)));
    rest.forEach((img, i) => galleryEl.appendChild(makeCard(img, i + featured.length)));

    if (images.length === 0) emptyEl.hidden = false;
  }

  function openLightbox(idx) {
    currentIndex = idx;
    const img = images[currentIndex];
    lbImg.src = img.raw_url;
    lbImg.alt = filenameToAlt(img.name);
    lbCap.textContent = img.name;
    lb.classList.add('open');
    lb.setAttribute('aria-hidden', 'false');
  }

  function closeLightbox() {
    lb.classList.remove('open');
    lb.setAttribute('aria-hidden', 'true');
    currentIndex = -1;
  }

  function nav(delta) {
    if (images.length === 0) return;
    currentIndex = (currentIndex + delta + images.length) % images.length;
    const img = images[currentIndex];
    lbImg.src = img.raw_url;
    lbImg.alt = filenameToAlt(img.name);
    lbCap.textContent = img.name;
  }

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // events
  btnClose.addEventListener('click', closeLightbox);
  btnPrev.addEventListener('click', () => nav(-1));
  btnNext.addEventListener('click', () => nav(1));
  lb.addEventListener('click', (e) => { if (e.target === lb) closeLightbox(); });
  document.addEventListener('keydown', (e) => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') nav(-1);
    if (e.key === 'ArrowRight') nav(1);
  });

  colControl.addEventListener('change', () => {
    document.querySelectorAll('.grid').forEach(g => g.style.setProperty('--col', colControl.value + 'px'));
  });

  shuffleBtn.addEventListener('click', () => {
    images = shuffle(images);
    render();
  });

  // init
  (async () => {
    try {
      const { owner, repo } = inferRepoInfo();
      const branch = await getDefaultBranch(owner, repo);
      images = await listImages(owner, repo, branch);
      render();
    } catch (err) {
      console.error(err);
      emptyEl.hidden = false;
      emptyEl.textContent = '載入圖片清單時發生錯誤。請確認此 Repository 為公開，且已建立 /images/ 目錄與圖片檔案。';
    }
  })();
})();
