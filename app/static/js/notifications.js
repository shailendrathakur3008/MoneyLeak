/**
 * MoneyLeak In-App Notification Bell & Browser Web Push Manager
 */

(function () {
  'use strict';

  // Helper to convert base64 VAPID public key to Uint8Array for PushManager
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // ---------------------------------------------------------------------------
  // 1. UNREAD BADGE & BELL DROPDOWN
  // ---------------------------------------------------------------------------
  async function fetchUnreadCount() {
    try {
      const res = await fetch('/api/notifications/unread-count');
      if (!res.ok) return;
      const data = await res.json();
      if (data.success) {
        updateBadgeUI(data.unread_count || 0);
      }
    } catch (e) {
      // Ignore network errors on background poll
    }
  }

  function updateBadgeUI(count) {
    const badges = document.querySelectorAll('.notification-unread-badge');
    badges.forEach((el) => {
      if (count > 0) {
        el.textContent = count > 99 ? '99+' : count;
        el.style.display = 'inline-flex';
      } else {
        el.textContent = '0';
        el.style.display = 'none';
      }
    });
  }

  async function loadBellDropdown() {
    const dropdownList = document.getElementById('notification-bell-dropdown-list');
    if (!dropdownList) return;

    dropdownList.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:12px;">Loading notifications...</div>';

    try {
      const res = await fetch('/api/notifications?per_page=5');
      if (!res.ok) throw new Error('Failed to load notifications');
      const data = await res.json();

      if (!data.success || !data.notifications || data.notifications.length === 0) {
        dropdownList.innerHTML = `
          <div style="padding:24px 16px;text-align:center;color:var(--text-muted);">
            <div style="font-size:20px;margin-bottom:6px;">🔔</div>
            <div style="font-weight:700;font-size:13px;color:var(--text-primary);">No notifications yet</div>
            <div style="font-size:11px;margin-top:2px;">Scheduled reminders will appear here.</div>
          </div>
        `;
        return;
      }

      dropdownList.innerHTML = data.notifications.map((n) => `
        <div class="bell-dropdown-item ${n.is_read ? '' : 'unread'}" onclick="handleNotificationClick(${n.id}, '${n.link_url || '/payments'}')">
          <div style="display:flex;align-items:flex-start;gap:10px;">
            <div class="bell-item-icon ${getChannelBadgeClass(n.notification_type)}">
              ${getNotificationIconHtml(n.notification_type)}
            </div>
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                <div class="bell-item-title">${escapeHtml(n.title)}</div>
                ${n.is_read ? '' : '<span class="bell-unread-dot"></span>'}
              </div>
              <div class="bell-item-msg">${escapeHtml(n.message)}</div>
              <div class="bell-item-time">${formatTimeAgo(n.scheduled_at)}</div>
            </div>
          </div>
        </div>
      `).join('');

      if (window.lucide) {
        lucide.createIcons();
      }
    } catch (e) {
      dropdownList.innerHTML = '<div style="padding:16px;text-align:center;color:var(--accent-red);font-size:12px;">Could not load notifications.</div>';
    }
  }

  window.handleNotificationClick = async function (id, targetUrl) {
    try {
      await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
      fetchUnreadCount();
    } catch (e) {}
    window.location.href = targetUrl || '/payments';
  };

  window.markAllNotificationsRead = async function () {
    try {
      const res = await fetch('/api/notifications/mark-all-read', { method: 'POST' });
      if (res.ok) {
        updateBadgeUI(0);
        loadBellDropdown();
        if (typeof window.loadNotificationsCenter === 'function') {
          window.loadNotificationsCenter();
        }
        if (window.showToast) {
          window.showToast('All notifications marked as read', 'success');
        }
      }
    } catch (e) {
      if (window.showToast) window.showToast('Failed to update notifications', 'danger');
    }
  };

  function getNotificationIconHtml(type) {
    if (type.includes('SIP')) return '<i data-lucide="trending-up" style="width:14px;height:14px;"></i>';
    if (type.includes('SUBSCRIPTION')) return '<i data-lucide="refresh-cw" style="width:14px;height:14px;"></i>';
    if (type.includes('EMI')) return '<i data-lucide="landmark" style="width:14px;height:14px;"></i>';
    if (type.includes('OVERDUE')) return '<i data-lucide="alert-triangle" style="width:14px;height:14px;color:#ef4444;"></i>';
    if (type.includes('CONFIRMED')) return '<i data-lucide="check-check" style="width:14px;height:14px;color:#10b981;"></i>';
    return '<i data-lucide="bell" style="width:14px;height:14px;"></i>';
  }

  function getChannelBadgeClass(type) {
    if (type.includes('OVERDUE') || type.includes('FAILED')) return 'badge-danger-soft';
    if (type.includes('CONFIRMED') || type.includes('PAID')) return 'badge-success-soft';
    if (type.includes('SIP')) return 'badge-lime-soft';
    return 'badge-primary-soft';
  }

  function formatTimeAgo(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);

    if (diffSec < 60) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ---------------------------------------------------------------------------
  // 2. BROWSER WEB PUSH PERMISSION & SUBSCRIPTION FLOW
  // ---------------------------------------------------------------------------
  window.enableBrowserPushNotifications = async function () {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      if (window.showToast) {
        window.showToast('Browser push notifications are not supported on this browser or platform.', 'warning');
      }
      return false;
    }

    try {
      // 1. Request user permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        if (window.showToast) {
          window.showToast('Push permission was denied. You can enable it in your browser site settings.', 'warning');
        }
        return false;
      }

      // 2. Retrieve VAPID public key
      let vapidKey = window.VAPID_PUBLIC_KEY;
      if (!vapidKey) {
        const keyRes = await fetch('/api/notifications/vapid-public-key');
        const keyData = await keyRes.json();
        if (keyData.success) {
          vapidKey = keyData.public_key;
        }
      }

      if (!vapidKey) {
        throw new Error('Could not retrieve VAPID public key from server.');
      }

      // 3. Register Service Worker at root scope
      const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      await navigator.serviceWorker.ready;

      // 4. Subscribe to PushManager
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey)
      });

      // 5. POST subscription details to backend
      const subJson = subscription.toJSON();
      const saveRes = await fetch('/api/notifications/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subJson)
      });

      const saveData = await saveRes.json();
      if (saveData.success) {
        if (window.showToast) {
          window.showToast('Browser push notifications successfully enabled!', 'success');
        }
        updatePushButtonsUI(true);
        return true;
      } else {
        throw new Error(saveData.error || 'Failed to save push subscription.');
      }
    } catch (err) {
      console.error('[WebPush] Error enabling push notifications:', err);
      if (window.showToast) {
        window.showToast(`Error enabling push: ${err.message}`, 'danger');
      }
      return false;
    }
  };

  function updatePushButtonsUI(enabled) {
    const pushBtns = document.querySelectorAll('.btn-enable-browser-push');
    pushBtns.forEach((btn) => {
      if (enabled) {
        btn.innerHTML = '<i data-lucide="check-circle" style="width:14px;height:14px;"></i> Notifications Enabled';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
        btn.disabled = true;
      }
    });

    const banner = document.getElementById('push-permission-banner');
    if (banner && enabled) {
      banner.style.display = 'none';
    }

    if (window.lucide) {
      lucide.createIcons();
    }
  }

  // ---------------------------------------------------------------------------
  // 3. INITIALIZATION & EVENT LISTENERS
  // ---------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch of unread count
    fetchUnreadCount();

    // Check existing push subscription status
    if ('Notification' in window && Notification.permission === 'granted') {
      updatePushButtonsUI(true);
    }

    // Toggle dropdown
    const bellBtn = document.getElementById('header-notification-bell-btn');
    const dropdown = document.getElementById('header-notification-dropdown');

    if (bellBtn && dropdown) {
      bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.style.display === 'block';
        dropdown.style.display = isOpen ? 'none' : 'block';
        if (!isOpen) {
          loadBellDropdown();
        }
      });

      document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && e.target !== bellBtn && !bellBtn.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    }

    // Poll unread count every 45 seconds while page is active
    setInterval(() => {
      if (!document.hidden) {
        fetchUnreadCount();
      }
    }, 45000);
  });
})();
