document.addEventListener('DOMContentLoaded', function() {
    // Ограничение даты в форме записи
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        const maxDate = new Date();
        maxDate.setMonth(maxDate.getMonth() + 3);
        const maxDateStr = maxDate.toISOString().split('T')[0];
        
        dateInput.min = today;
        dateInput.max = maxDateStr;
    }
});