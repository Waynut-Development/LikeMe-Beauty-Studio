document.addEventListener('DOMContentLoaded', function() {
    // Элементы интерфейса
    const weekNavigation = document.querySelector('.week-navigation');
    const scheduleGrid = document.querySelector('.schedule-grid');
    
    // Обработчики событий
    if (weekNavigation) {
        weekNavigation.addEventListener('click', handleWeekNavigation);
    }
    
    if (scheduleGrid) {
        scheduleGrid.addEventListener('click', handleSlotActions);
    }
    
    // Функции
    function handleWeekNavigation(event) {
        event.preventDefault();
        if (event.target.tagName === 'A') {
            // Показываем индикатор загрузки
            showLoadingIndicator();
            window.location.href = event.target.href;
        }
    }
    
    function handleSlotActions(event) {
        const target = event.target;
        
        if (target.classList.contains('free-btn')) {
            event.preventDefault();
            freeTimeSlot(target);
        } 
        else if (target.classList.contains('book-btn')) {
            event.preventDefault();
            bookTimeSlot(target);
        }
    }
    
    function freeTimeSlot(button) {
        const slot = button.closest('.time-slot');
        const appointmentId = button.dataset.id;
        
        // Подтверждение действия
        if (!confirm('Вы уверены, что хотите освободить это время?')) {
            return;
        }
        
        // Показываем индикатор загрузки на слоте
        showSlotLoading(slot, true);
        
        fetch('/admin/api/free-slot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ id: appointmentId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Обновляем интерфейс
                updateSlotToFree(slot);
                showToast('Время успешно освобождено', 'success');
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error freeing slot:', error);
            showToast('Ошибка освобождения времени: ' + error.message, 'error');
        })
        .finally(() => {
            hideSlotLoading(slot);
        });
    }
    
    function bookTimeSlot(button) {
        const slot = button.closest('.time-slot');
        const date = slot.dataset.date;
        const time = slot.dataset.time;
        
        // Подтверждение действия
        if (!confirm('Вы уверены, что хотите заблокировать это время?')) {
            return;
        }
        
        // Показываем индикатор загрузки на слоте
        showSlotLoading(slot, true);
        
        fetch('/admin/api/block-slot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ date, time })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Обновляем интерфейс
                updateSlotToBooked(slot, data.appointment_id);
                showToast('Время успешно заблокировано', 'success');
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error booking slot:', error);
            showToast('Ошибка блокировки времени: ' + error.message, 'error');
        })
        .finally(() => {
            hideSlotLoading(slot);
        });
    }
    
    // Вспомогательные функции
    function updateSlotToFree(slot) {
        slot.classList.remove('booked');
        slot.classList.add('free');
        
        const statusDiv = slot.querySelector('.status');
        statusDiv.innerHTML = `
            <span class="status-badge free">Свободно</span>
            <button class="btn book-btn">Заблокировать</button>
        `;
        
        // Добавляем анимацию
        slot.style.animation = 'none';
        void slot.offsetWidth; // Trigger reflow
        slot.style.animation = 'fadeIn 0.5s ease-out';
    }
    
    function updateSlotToBooked(slot, appointmentId) {
        slot.classList.remove('free');
        slot.classList.add('booked');
        
        const statusDiv = slot.querySelector('.status');
        statusDiv.innerHTML = `
            <span class="status-badge booked">Заблокировано</span>
            <button class="btn free-btn" data-id="${appointmentId}">Освободить</button>
        `;
        
        // Добавляем анимацию
        slot.style.animation = 'none';
        void slot.offsetWidth; // Trigger reflow
        slot.style.animation = 'pulse 0.5s ease-out';
    }
    
    function showSlotLoading(slot, show) {
        const loadingIndicator = slot.querySelector('.loading-indicator') || 
            document.createElement('div');
            
        if (show) {
            loadingIndicator.className = 'loading-indicator';
            loadingIndicator.innerHTML = '<div class="spinner"></div>';
            slot.appendChild(loadingIndicator);
            slot.querySelector('.status').style.visibility = 'hidden';
        } else {
            if (slot.querySelector('.loading-indicator')) {
                slot.removeChild(loadingIndicator);
            }
            slot.querySelector('.status').style.visibility = 'visible';
        }
    }
    
    function showLoadingIndicator() {
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.innerHTML = `
            <div class="loader-overlay"></div>
            <div class="loader-content">
                <div class="spinner"></div>
                <p>Загрузка...</p>
            </div>
        `;
        document.body.appendChild(loader);
    }
    
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // CSS анимации
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .loading-indicator {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.8);
            z-index: 10;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top-color: #d4af37;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 24px;
            border-radius: 4px;
            color: white;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
        }
        
        .toast.show {
            opacity: 1;
        }
        
        .toast-success {
            background-color: #4CAF50;
        }
        
        .toast-error {
            background-color: #f44336;
        }
        
        #global-loader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
        }
        
        .loader-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.2);
        }
        
        .loader-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
    `;
    document.head.appendChild(style);
});