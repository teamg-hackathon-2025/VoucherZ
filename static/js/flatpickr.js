document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.js-flatpickr').forEach(el => {
    if (el._flatpickr) return;

    flatpickr(el, {
      dateFormat: 'Y-m-d',
      minDate: el.dataset.min || 'today',
      locale: flatpickr.l10ns.ja,
      disableMobile: true,
      onInput(selectedDates, dateStr, instance) {
        if (instance.input.value.trim() === '') instance.clear();
      },
      onReady(selectedDates, dateStr, instance) {
        const footer = document.createElement('div');
        footer.className = 'flatpickr-footer';
        // クリアボタン
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'flatpickr-clear';
        btn.textContent = 'クリア';
        btn.addEventListener('click', () => {
          instance.clear();
          instance.close();
        });
        footer.appendChild(btn);
        instance.calendarContainer.appendChild(footer);
      }
    });
  });
});