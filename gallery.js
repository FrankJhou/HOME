/* Auto-populating gallery for GitHub Pages
 * It lists files in /images via GitHub REST API without any build step.
 * Requirements: public repo; images placed under /images.
 */
(async () => {
  const galleryEl = document.getElementById('gallery');
  const emptyEl = document.getElementById('emptyState');
  const tpl = document.getElementById('cardTpl');

  // Infer owner and repo from current URL
  function inferRepoInfo() {
    const host = window.location.hostname;  // e.g., username.github.io
    const path = window.location.pathname.replace(/^\//, ''); // e.g., repo/ or "" for user site root
    const owner = host.split('.')[0];
    let repo = '';
    if (!path || path.split('/')[0] === '') {
      // root site: repo name is username.github.io
      repo = `${owner}.github.io`;
    } else {
      repo = path.split('/')[0];
    }
    return { owner, repo };
  }

  // Get default branch (main/master/etc.)
  async function getDefaultBranch(owner, repo) {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`);
    if (!res.ok) throw new Error('無法取得 Repository 資訊：' + res.status);
    const data = await res.json();
    return data.default_branch || 'main';
  }

  // List contents of /images on the default branch
  async function listImages(owner, repo, branch, dir = 'images') {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(dir)}?ref=${encodeURIComponent(branch)}`);
    if (res.status === 404) return []; // no images folder yet
    if (!res.ok) throw new Error('讀取 /images 失敗：' + res.status);
    const items = await res.json();
    const exts = new Set(['.jpg','.jpeg','.png','.gif','.webp','.avif','.JPG','.JPEG','.PNG','.GIF','.WEBP','.AVIF']);
    return items
      .filter(it => it.type === 'file' && [...exts].some(ext => it.name.endsWith(ext)))
      .map(it => ({
        name: it.name,
        download_url: it.download_url,
        // Use raw.githubusercontent URL for better performance; fallback to download_url if needed
        raw_url: `https://raw.githubusercontent.com/${owner}/${repo}/${encodeURIComponent(branch)}/images/${encodeURIComponent(it.name)}`
      }));
  }

  function filenameToAlt(name) {
    return name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
  }

  try {
    const { owner, repo } = inferRepoInfo();
    const branch = await getDefaultBranch(owner, repo);
    const images = await listImages(owner, repo, branch);

    if (!images.length) {
      emptyEl.hidden = false;
      return;
    }

    images.forEach(img => {
      const node = tpl.content.firstElementChild.cloneNode(true);
      const a = node.querySelector('.card-link');
      const image = node.querySelector('img');
      const cap = node.querySelector('figcaption');
      a.href = img.raw_url;
      image.src = img.raw_url;
      image.alt = filenameToAlt(img.name);
      cap.textContent = img.name;
      galleryEl.appendChild(node);
    });
  } catch (err) {
    console.error(err);
    emptyEl.hidden = false;
    emptyEl.textContent = '載入圖片清單時發生錯誤。請確認此 Repository 為公開，且已建立 /images/ 目錄與圖片檔案。';
  }
})();
