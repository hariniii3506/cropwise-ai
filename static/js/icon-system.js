// =============================================================================
// CROPWISE AI - Vector Outline Icon Replacement Engine (icon-system.js)
// =============================================================================
// Maps Unicode emojis and data attributes across the DOM to lightweight,
// crisp SVG outline icons for agricultural, weather, financial, and navigation items.
// =============================================================================

/* CROPWISE AI shared outline icon system. */
(() => {
  const codePoint = (...values) => String.fromCodePoint(...values);
  const icons = new Map([
    [codePoint(0x1f331), ['plant', 'M3 20V9m0 4c-3-1-4-3-4-6 3 0 5 1 6 4m-2 1c1-4 4-6 8-6 0 4-2 7-6 8']],
    [codePoint(0x1f33e), ['crop', 'M4 20h16M6 20V8m6 12V4m6 16v-9M4 8h4m4-4h4m4 7h-4']],
    [codePoint(0x1f916), ['ai', 'M8 8h8a2 2 0 0 1 2 2v6H6v-6a2 2 0 0 1 2-2Zm-2 4H4m16 0h-2M10 5V3m4 2V3M9 12h.01M15 12h.01M9 16h6']],
    [codePoint(0x1f4a7), ['water', 'M12 3s6 6.2 6 10a6 6 0 1 1-12 0c0-3.8 6-10 6-10Zm-3 11a3 3 0 0 0 3 3']],
    [codePoint(0x1f4ca), ['chart', 'M4 19V5m0 14h16M8 16v-5m4 5V7m4 9v-8']],
    [codePoint(0x1f4c5), ['calendar', 'M5 4h14a2 2 0 0 1 2 2v13H3V6a2 2 0 0 1 2-2Zm3-2v4m8-4v4M3 9h18']],
    [codePoint(0x1f4b0), ['money', 'M3 6h18v12H3zM7 12h.01M17 12h.01M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z']],
    [codePoint(0x1f4be), ['save', 'M5 3h12l2 2v16H5V3Zm3 0v6h8V3M8 21v-7h8v7']],
    [codePoint(0x1f4d2), ['ledger', 'M5 3h12a2 2 0 0 1 2 2v16H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm3 4h7m-7 4h7m-7 4h5']],
    [codePoint(0x1f464), ['user', 'M20 21a8 8 0 0 0-16 0m8-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z']],
    [codePoint(0x1f321), ['temperature', 'M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0ZM12 5v10']],
    [codePoint(0x1f327), ['weather', 'M7 18h10a4 4 0 1 0-1-7.9A5 5 0 0 0 6 11a3.5 3.5 0 0 0 1 7Zm-1-2h.01']],
      [codePoint(0x1f326, 0xfe0f), ['weather', 'M7 18h10a4 4 0 1 0-1-7.9A5 5 0 0 0 6 11a3.5 3.5 0 0 0 1 7Zm-1-2h.01']],
    [codePoint(0x1f9ea), ['soil', 'M8 3h8m-7 0v5l-3 9a2 2 0 0 0 2 3h8a2 2 0 0 0 2-3l-3-9V3m-6 8h6']],
    [codePoint(0x1f4cb), ['report', 'M7 3h10v18H7zM9 7h6m-6 4h6m-6 4h4']],
      [codePoint(0x1f4dd), ['note', 'M5 3h14v18H5zM8 7h8m-8 4h8m-8 4h5']],
    [codePoint(0x2699, 0xfe0f), ['settings', 'M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm7.4-3.5 1.1.9-1.6 2.8-1.3-.5a7.6 7.6 0 0 1-1.5.9L14 18v3h-4v-3l-1.1-.4a7.6 7.6 0 0 1-1.5-.9l-1.3.5-1.6-2.8 1.1-.9a7 7 0 0 1 0-1.8l-1.1-.9 1.6-2.8 1.3.5a7.6 7.6 0 0 1 1.5-.9L10 8V5h4v3l1.1.4a7.6 7.6 0 0 1 1.5.9l1.3-.5 1.6 2.8-1.1.9a7 7 0 0 1 0 1.8Z']],
    [codePoint(0x1f3e0), ['home', 'M3 11 12 3l9 8v9H3v-9Zm6 9v-6h6v6']],
      [codePoint(0x1f3e1), ['home', 'M3 11 12 3l9 8v9H3v-9Zm6 9v-6h6v6']],
    [codePoint(0x1f504), ['refresh', 'M20 11a8 8 0 0 0-14.9-4L3 10m0 0V4m0 6h6M4 13a8 8 0 0 0 14.9 4L21 14m0 0v6m0-6h-6']],
    [codePoint(0x23f1, 0xfe0f), ['clock', 'M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z']],
    [codePoint(0x1f4dc), ['document', 'M6 3h9l4 4v14H6V3Zm9 0v5h4M9 12h6m-6 4h6']],
    [codePoint(0x1f5a8, 0xfe0f), ['printer', 'M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2v3H6v-3Zm3-5h6']],
    [codePoint(0x1f3db, 0xfe0f), ['government', 'M3 21h18M5 18h14M4 9h16L12 3 4 9Zm3 2v4m5-4v4m5-4v4']],
    [codePoint(0x2139, 0xfe0f), ['info', 'M12 16v-4m0-4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z']],
    [codePoint(0x2705), ['check', 'm5 12 4 4L19 6']],
    [codePoint(0x26a0, 0xfe0f), ['warning', 'M12 3 2 21h20L12 3Zm0 6v5m0 3h.01']],
    [codePoint(0x1f310), ['globe', 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-18c2.2 2.4 3.3 5.4 3.3 9S14.2 18.6 12 21m0-18C9.8 5.4 8.7 8.4 8.7 12s1.1 6.6 3.3 9M3 12h18']],
    [codePoint(0x1f441, 0xfe0f), ['eye', 'M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Zm10 3a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z']],
    [codePoint(0x1f648), ['eye-off', 'M3 3l18 18M10.6 6.2A10.8 10.8 0 0 1 12 6c6.5 0 10 6 10 6a17.5 17.5 0 0 1-4.2 4.5M6.2 6.2C3.5 8.4 2 12 2 12s3.5 6 10 6a9.8 9.8 0 0 0 3.4-.6']],
    [codePoint(0x2795), ['plus', 'M12 5v14M5 12h14']],
    [codePoint(0x1f4cc), ['pin', 'm12 17 5-5a5 5 0 1 0-10 0l5 5Zm0 0v4']],
    [codePoint(0x1f393), ['education', 'M3 9l9-4 9 4-9 4-9-4Zm3 2v5c3 2 9 2 12 0v-5']],
    [codePoint(0x1f3a8), ['education', 'M3 9l9-4 9 4-9 4-9-4Zm3 2v5c3 2 9 2 12 0v-5']],
    [codePoint(0x1f4f1), ['mobile', 'M7 2h10v20H7zM11 19h2']],
    [codePoint(0x1f4e1), ['signal', 'M4 20h2v-5H4v5Zm7 0h2V9h-2v11Zm7 0h2V3h-2v17Z']],
    [codePoint(0x1f4c8), ['trend', 'M3 17l6-6 4 4 8-9M16 6h5v5']],
    [codePoint(0x1f4b9), ['trend', 'M3 17l6-6 4 4 8-9M16 6h5v5']],
      [codePoint(0x1f4a1), ['idea', 'M9 18h6m-5 3h4M8 14a6 6 0 1 1 8 0c-1 1-1 2-1 4H9c0-2 0-3-1-4Z']],
      [codePoint(0x1f9e0), ['ai', 'M8 8h8a2 2 0 0 1 2 2v6H6v-6a2 2 0 0 1 2-2Zm-2 4H4m16 0h-2M10 5V3m4 2V3M9 12h.01M15 12h.01M9 16h6']],
      [codePoint(0x1f680), ['launch', 'm4 20 4-1 9-9a4 4 0 0 0-5.7-5.7l-9 9-1 4 4-1Zm5-13 3 3M4 14l-2 2 4 4 2-2']],
      [codePoint(0x1f5e3, 0xfe0f), ['voice', 'M12 15a3 3 0 0 0 3-3V7a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm-6-3a6 6 0 0 0 12 0m-6 6v3m-4 0h8']],
      [codePoint(0x1f468, 0x1f33e), ['user', 'M20 21a8 8 0 0 0-16 0m8-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z']],
      [codePoint(0x1f9d1, 0x1f33e), ['user', 'M20 21a8 8 0 0 0-16 0m8-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z']],
      [codePoint(0x1f9d1, 0x200d, 0x1f33e), ['user', 'M20 21a8 8 0 0 0-16 0m8-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z']],
  ]);

  const tokens = [...icons.keys()].sort((a, b) => b.length - a.length);
  const ignoredParents = new Set(['SCRIPT', 'STYLE', 'SVG', 'TEXTAREA', 'OPTION']);

  function makeIcon(name, path) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', `ui-icon ui-icon-${name}`);
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.8');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    svg.dataset.icon = name;
    const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathElement.setAttribute('d', path);
    svg.appendChild(pathElement);
    return svg;
  }

  function replaceNode(node) {
    const raw = node.nodeValue || '';
    const leading = raw.match(/^\s*/)[0];
    const content = raw.slice(leading.length);
    const token = tokens.find((candidate) => content.startsWith(candidate));
    if (!token) return;
    const [name, path] = icons.get(token);
    const fragment = document.createDocumentFragment();
    if (leading) fragment.appendChild(document.createTextNode(leading));
    fragment.appendChild(makeIcon(name, path));
    const remaining = content.slice(token.length);
    if (remaining) fragment.appendChild(document.createTextNode(remaining));
    node.replaceWith(fragment);
  }

  function normalizeIcons(root = document.body) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) {
      if (!node.parentElement || ignoredParents.has(node.parentElement.tagName)) continue;
      nodes.push(node);
    }
    nodes.forEach(replaceNode);
  }

  window.CropwiseIcons = { normalizeIcons, makeIcon };
  document.addEventListener('DOMContentLoaded', () => normalizeIcons());
  window.addEventListener('languageChanged', () => normalizeIcons());

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((added) => {
        if (added.nodeType === Node.TEXT_NODE) replaceNode(added);
        else if (added.nodeType === Node.ELEMENT_NODE && !added.matches('svg')) normalizeIcons(added);
      });
    });
  });
  document.addEventListener('DOMContentLoaded', () => observer.observe(document.body, { childList: true, subtree: true }));
})();
