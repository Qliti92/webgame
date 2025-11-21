/**
 * Notification System for Game TopUp
 * Handles: bell icon badge, dropdown, toast notifications
 */

class NotificationManager {
    constructor() {
        this.apiBaseUrl = '/api/notifications';
        this.pollingInterval = 30000; // 30 seconds
        this.pollingTimer = null;
        this.notifications = [];
        this.unreadCount = 0;
        this.isDropdownOpen = false;
        this.toastQueue = [];
        this.maxToasts = 3;

        this.init();
    }

    init() {
        // Check if user is logged in
        const token = localStorage.getItem('access_token');
        if (!token) {
            return;
        }

        this.createNotificationElements();
        this.bindEvents();
        this.fetchUnreadCount();
        this.checkImportantNotifications();
        this.startPolling();
    }

    createNotificationElements() {
        // Create notification container in header if not exists
        const headerNav = document.querySelector('header nav .flex.justify-between');
        if (!headerNav) return;

        // Find the desktop auth buttons container
        const desktopAuthContainer = document.querySelector('.hidden.md\\:flex.items-center.space-x-3');
        if (!desktopAuthContainer) return;

        // Create notification bell (desktop)
        const bellContainer = document.createElement('div');
        bellContainer.id = 'notification-container';
        bellContainer.className = 'relative';
        bellContainer.innerHTML = `
            <button id="notification-bell" class="relative p-2 text-dark-300 hover:text-white transition-colors" aria-label="Notifications">
                <i class="fas fa-bell text-xl"></i>
                <span id="notification-badge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">0</span>
            </button>
            <div id="notification-dropdown" class="absolute right-0 mt-2 w-80 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50 hidden">
                <div class="p-3 border-b border-dark-700 flex justify-between items-center">
                    <h3 class="font-semibold text-white">Notifications</h3>
                    <button id="mark-all-read" class="text-xs text-primary-400 hover:text-primary-300">Mark all read</button>
                </div>
                <div id="notification-list" class="max-h-96 overflow-y-auto">
                    <div class="p-4 text-center text-dark-400">Loading...</div>
                </div>
                <div class="p-2 border-t border-dark-700">
                    <a href="/notifications/" class="block text-center text-sm text-primary-400 hover:text-primary-300 py-2">View all notifications</a>
                </div>
            </div>
        `;

        // Insert before the first auth button
        desktopAuthContainer.insertBefore(bellContainer, desktopAuthContainer.firstChild);

        // Create toast container
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed top-20 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }
    }

    bindEvents() {
        // Bell click
        const bell = document.getElementById('notification-bell');
        if (bell) {
            bell.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        // Mark all read
        const markAllBtn = document.getElementById('mark-all-read');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => this.markAllAsRead());
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const container = document.getElementById('notification-container');
            if (container && !container.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });
    }

    getAuthHeaders() {
        const token = localStorage.getItem('access_token');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async fetchUnreadCount() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/unread_count/`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.updateBadge(data.count);
            }
        } catch (error) {
            console.error('Failed to fetch unread count:', error);
        }
    }

    async fetchRecentNotifications() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/recent/?limit=10`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.notifications = data.results;
                this.updateBadge(data.unread_count);
                this.renderNotificationList();
            }
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
        }
    }

    async checkImportantNotifications() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/important/`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const notifications = await response.json();

                // Get already shown toast IDs from localStorage
                const shownToasts = JSON.parse(localStorage.getItem('shown_toast_ids') || '[]');

                // Filter out notifications that have already been shown as toast
                const newNotifications = notifications.filter(n => !shownToasts.includes(n.id));

                // Show toasts for new important notifications
                newNotifications.forEach(notification => {
                    this.showToast(notification);
                });

                // Save shown toast IDs to localStorage and mark as read
                if (newNotifications.length > 0) {
                    const newIds = newNotifications.map(n => n.id);

                    // Update localStorage with new shown IDs (keep last 100 to prevent bloat)
                    const updatedShownToasts = [...shownToasts, ...newIds].slice(-100);
                    localStorage.setItem('shown_toast_ids', JSON.stringify(updatedShownToasts));

                    // Mark as read
                    this.markAsRead(newIds);
                }
            }
        } catch (error) {
            console.error('Failed to fetch important notifications:', error);
        }
    }

    async markAsRead(notificationIds) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/mark_as_read/`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ notification_ids: notificationIds })
            });

            if (response.ok) {
                this.fetchUnreadCount();
            }
        } catch (error) {
            console.error('Failed to mark as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/mark_all_read/`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.updateBadge(0);
                this.fetchRecentNotifications();
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    }

    updateBadge(count) {
        this.unreadCount = count;
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }

    toggleDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            if (this.isDropdownOpen) {
                this.closeDropdown();
            } else {
                this.openDropdown();
            }
        }
    }

    openDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.classList.remove('hidden');
            this.isDropdownOpen = true;
            this.fetchRecentNotifications();
        }
    }

    closeDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
            this.isDropdownOpen = false;
        }
    }

    renderNotificationList() {
        const list = document.getElementById('notification-list');
        if (!list) return;

        if (this.notifications.length === 0) {
            list.innerHTML = `
                <div class="p-8 text-center text-dark-400">
                    <i class="fas fa-bell-slash text-3xl mb-2"></i>
                    <p>No notifications yet</p>
                </div>
            `;
            return;
        }

        list.innerHTML = this.notifications.map(notification => `
            <div class="notification-item p-3 hover:bg-dark-700 cursor-pointer border-b border-dark-700/50 ${!notification.is_read ? 'bg-dark-700/30' : ''}"
                 data-id="${notification.id}"
                 data-order-id="${notification.order_id || ''}"
                 data-transaction-id="${notification.transaction_id || ''}">
                <div class="flex items-start">
                    <div class="flex-shrink-0 mr-3">
                        ${this.getNotificationIcon(notification.notification_type)}
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-white truncate">${notification.title}</p>
                        <p class="text-xs text-dark-400 mt-1 line-clamp-2">${notification.message}</p>
                        <p class="text-xs text-dark-500 mt-1">${notification.time_ago}</p>
                    </div>
                    ${!notification.is_read ? '<span class="w-2 h-2 bg-primary-500 rounded-full ml-2"></span>' : ''}
                </div>
            </div>
        `).join('');

        // Add click handlers
        list.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.dataset.id;
                const orderId = item.dataset.orderId;
                const transactionId = item.dataset.transactionId;

                // Mark as read
                this.markAsRead([parseInt(id)]);

                // Navigate to relevant page
                if (orderId) {
                    window.location.href = `/orders/${orderId}/`;
                } else if (transactionId) {
                    window.location.href = `/wallet/deposits/`;
                }

                this.closeDropdown();
            });
        });
    }

    getNotificationIcon(type) {
        const icons = {
            'ORDER': '<i class="fas fa-shopping-cart text-blue-400"></i>',
            'DEPOSIT': '<i class="fas fa-arrow-down text-green-400"></i>',
            'WITHDRAW': '<i class="fas fa-arrow-up text-yellow-400"></i>',
            'SYSTEM': '<i class="fas fa-info-circle text-purple-400"></i>'
        };
        return icons[type] || icons['SYSTEM'];
    }

    showToast(notification) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        // Limit active toasts
        const activeToasts = container.children.length;
        if (activeToasts >= this.maxToasts) {
            // Remove oldest toast
            container.removeChild(container.firstChild);
        }

        const toast = document.createElement('div');
        toast.className = 'toast bg-dark-800 border border-dark-700 rounded-lg shadow-lg p-4 max-w-sm transform translate-x-0 transition-all duration-300';
        toast.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 mr-3">
                    ${this.getNotificationIcon(notification.notification_type)}
                </div>
                <div class="flex-1">
                    <p class="text-sm font-medium text-white">${notification.title}</p>
                    <p class="text-xs text-dark-400 mt-1">${notification.message}</p>
                </div>
                <button class="toast-close ml-2 text-dark-400 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Click to navigate
        toast.addEventListener('click', (e) => {
            if (!e.target.closest('.toast-close')) {
                if (notification.order_id) {
                    window.location.href = `/orders/${notification.order_id}/`;
                } else if (notification.transaction_id) {
                    window.location.href = `/wallet/deposits/`;
                }
            }
        });

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
    }

    removeToast(toast) {
        if (toast && toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }

    startPolling() {
        this.pollingTimer = setInterval(() => {
            this.fetchUnreadCount();
            this.checkImportantNotifications();
        }, this.pollingInterval);
    }

    stopPolling() {
        if (this.pollingTimer) {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;
        }
    }

    destroy() {
        this.stopPolling();
        const container = document.getElementById('notification-container');
        if (container) {
            container.remove();
        }
        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            toastContainer.remove();
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.notificationManager = new NotificationManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.notificationManager) {
        window.notificationManager.stopPolling();
    }
});
