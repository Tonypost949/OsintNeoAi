const panel = document.querySelector('.signal-panel');
const nodes = document.querySelectorAll('.signal-node');

panel?.addEventListener('pointermove', (event) => {
  const rect = panel.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width - 0.5) * 8;
  const y = ((event.clientY - rect.top) / rect.height - 0.5) * 8;
  nodes.forEach((node, index) => {
    node.style.transform = `translate(${x * (index + 1) / 2}px, ${y * (index + 1) / 2}px)`;
  });
});

panel?.addEventListener('pointerleave', () => {
  nodes.forEach((node) => { node.style.transform = ''; });
});
