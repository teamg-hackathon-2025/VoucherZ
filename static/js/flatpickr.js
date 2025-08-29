document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.js-flatpickr').forEach(el => {
    if (el._flatpickr) return;

    flatpickr(el, {
      dateFormat: 'Y-m-d',
      minDate: el.dataset.min || 'today',
      locale: flatpickr.l10ns.ja,
      disableMobile: true,
      altInput: true,
      altFormat: 'Y/m/d',
      onInput(selectedDates, dateStr, instance) {
        if (instance.input.value.trim() === '') instance.clear();
      },
      onReady(selectedDates, dateStr, instance) {
        const footer = document.createElement('div');
        footer.className = 'flatpickr-footer';
        // 削除ボタン
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'flatpickr-clear';
        button.textContent = '日付削除';
        button.addEventListener('click', () => {
          instance.clear();
          instance.close();
        });
        footer.appendChild(button);
        instance.calendarContainer.appendChild(footer);
      }
    });
  });
});