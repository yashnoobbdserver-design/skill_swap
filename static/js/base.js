// Mobile menu toggle
if (document.getElementById('mobileMenuBtn')) {
    document.getElementById('mobileMenuBtn').addEventListener('click', function() {
        const menu = document.getElementById('mobileMenu');
        menu.classList.toggle('hidden');
    });
}

// User menu dropdown
if (document.getElementById('userMenuBtn')) {
    document.getElementById('userMenuBtn').addEventListener('click', function() {
        const dropdown = document.getElementById('userMenuDropdown');
        dropdown.classList.toggle('hidden');
    });
}

// Notification dropdown
if (document.getElementById('notificationBtn')) {
    document.getElementById('notificationBtn').addEventListener('click', function() {
        const dropdown = document.getElementById('notificationDropdown');
        dropdown.classList.toggle('hidden');
        if (!dropdown.classList.contains('hidden')) {
            loadNotifications();
        }
    });
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('userMenuDropdown');
    const userBtn = document.getElementById('userMenuBtn');
    const notificationMenu = document.getElementById('notificationDropdown');
    const notificationBtn = document.getElementById('notificationBtn');
    if (userBtn && !userBtn.contains(event.target)) {
        userMenu && userMenu.classList.add('hidden');
    }
    if (notificationBtn && !notificationBtn.contains(event.target)) {
        notificationMenu && notificationMenu.classList.add('hidden');
    }
});

// Load notifications via AJAX
function loadNotifications() {
    if (window.isAuthenticated) {
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                updateNotificationCount(data.unread_count);
                displayNotifications(data.notifications);
            })
            .catch(error => console.error('Error loading notifications:', error));
    }
}

function updateNotificationCount(count) {
    const badge = document.getElementById('notificationCount');
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function displayNotifications(notifications) {
    const list = document.getElementById('notificationList');
    if (!list) return;
    if (notifications.length === 0) {
        list.innerHTML = '<p class="p-4 text-gray-500 text-center">No notifications</p>';
        return;
    }
    list.innerHTML = notifications.map(notification => `
        <div class="p-3 border-b hover:bg-gray-50 ${!notification.is_read ? 'bg-blue-50' : ''}">
            <div class="flex justify-between items-start">
                <div>
                    <h6 class="font-medium text-gray-800">${notification.title}</h6>
                    <p class="text-sm text-gray-600">${notification.message}</p>
                    <span class="text-xs text-gray-400">${notification.created_at}</span>
                </div>
                ${!notification.is_read ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
            </div>
        </div>
    `).join('');
}

// Load notification count on page load
if (window.isAuthenticated) {
    fetch('/api/notifications/unread-count/')
        .then(response => response.json())
        .then(data => updateNotificationCount(data.count))
        .catch(error => console.error('Error loading notification count:', error));
}