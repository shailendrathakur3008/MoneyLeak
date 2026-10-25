/**
 * MoneyLeak Service Worker for Browser Web Push Notifications.
 * Listens for push messages dispatched by the server and handles notification clicks.
 */

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  if (!event.data) {
    return;
  }

  let payload = {};
  try {
    payload = event.data.json();
  } catch (err) {
    payload = {
      title: 'MoneyLeak Reminder',
      body: event.data.text()
    };
  }

  const title = payload.title || 'MoneyLeak Payment Reminder';
  const options = {
    body: payload.body || 'You have an upcoming scheduled payment obligation.',
    icon: payload.icon || '/static/icons/icon-192.png',
    badge: payload.badge || '/static/icons/badge-72.png',
    tag: payload.tag || 'moneyleak-payment-reminder',
    renotify: true,
    data: payload.data || { url: '/payments' },
    actions: [
      { action: 'view', title: 'View Payment' },
      { action: 'dismiss', title: 'Close' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'dismiss') {
    return;
  }

  const targetUrl = (event.notification.data && event.notification.data.url) || '/payments';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // If a tab is already open, focus it and navigate
      for (const client of clientList) {
        if (client.url && 'focus' in client) {
          if ('navigate' in client) {
            client.navigate(targetUrl);
          }
          return client.focus();
        }
      }
      // Otherwise open a new browser window
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
    })
  );
});
