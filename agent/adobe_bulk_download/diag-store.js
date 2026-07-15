// diag-store.js — Thin IndexedDB wrapper for diagnostic log storage.
// Provides: open, batchAdd, getAll, iterateAll, deleteOlderThan, trimToMax, count, clear.
// No library dependency. Promise-based wrapper around raw IDB API.
// Shared origin: both the service worker and sidepanel can import and use this module.

import { config } from './config.js';

const DB_VERSION = 1;
let _dbPromise = null;

/**
 * Lazy-open the diagnostics IndexedDB. Returns a cached promise.
 * Resets the cached promise on error so the next call retries.
 */
export function openDb() {
  if (_dbPromise) return _dbPromise;
  _dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(config.diagDbName, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(config.diagStoreName)) {
        const store = db.createObjectStore(config.diagStoreName, { autoIncrement: true });
        store.createIndex('ts', 'ts', { unique: false });
        store.createIndex('level', 'level', { unique: false });
      }
    };
    req.onsuccess = (e) => {
      const db = e.target.result;
      db.onversionchange = () => { db.close(); _dbPromise = null; };
      db.onclose = () => { _dbPromise = null; };
      resolve(db);
    };
    req.onerror = () => { _dbPromise = null; reject(req.error); };
    req.onblocked = () => { _dbPromise = null; reject(new Error('IDB open blocked')); };
  });
  return _dbPromise;
}

/**
 * Add an array of entries in a single readwrite transaction.
 * @param {Array<Object>} entries
 */
export async function batchAdd(entries) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readwrite', { durability: 'relaxed' });
    const store = tx.objectStore(config.diagStoreName);
    for (const entry of entries) store.add(entry);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error || new Error('Transaction aborted'));
  });
}

/**
 * Get all entries (optionally limited to last N via cursor).
 * @param {number} [limit] — if provided, returns only the last `limit` entries
 * @returns {Promise<Array<Object>>}
 */
export async function getAll(limit) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readonly');
    const store = tx.objectStore(config.diagStoreName);
    if (limit == null) {
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    } else {
      // Walk backwards from the end to get last N entries
      const results = [];
      const req = store.openCursor(null, 'prev');
      req.onsuccess = (e) => {
        const cursor = e.target.result;
        if (cursor && results.length < limit) {
          results.push(cursor.value);
          cursor.continue();
        } else {
          resolve(results.reverse());
        }
      };
      req.onerror = () => reject(req.error);
    }
  });
}

/**
 * Count total entries in the store.
 * @returns {Promise<number>}
 */
export async function count() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readonly');
    const req = tx.objectStore(config.diagStoreName).count();
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

/**
 * Delete entries older than a given timestamp using the 'ts' index.
 * @param {number} maxAgeTs — delete entries where ts < maxAgeTs
 * @returns {Promise<number>} — number of entries deleted
 */
export async function deleteOlderThan(maxAgeTs) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readwrite');
    const index = tx.objectStore(config.diagStoreName).index('ts');
    const range = IDBKeyRange.upperBound(maxAgeTs, true);
    let deleted = 0;
    const req = index.openCursor(range);
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor) {
        const delReq = cursor.delete();
        delReq.onerror = (evt) => { evt.preventDefault(); evt.stopPropagation(); };
        deleted++;
        cursor.continue();
      }
    };
    tx.oncomplete = () => resolve(deleted);
    tx.onerror = () => reject(tx.error);
  });
}

/**
 * Trim to maxEntries by deleting the oldest entries (by auto-increment key).
 * @param {number} maxEntries
 * @returns {Promise<number>} — number of entries deleted
 */
export async function trimToMax(maxEntries) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readwrite');
    const store = tx.objectStore(config.diagStoreName);
    const countReq = store.count();
    let deleted = 0;
    countReq.onsuccess = () => {
      const total = countReq.result;
      if (total <= maxEntries) return;
      const excess = total - maxEntries;
      const cursorReq = store.openCursor();
      cursorReq.onsuccess = (e) => {
        const cursor = e.target.result;
        if (cursor && deleted < excess) { cursor.delete(); deleted++; cursor.continue(); }
      };
    };
    tx.oncomplete = () => resolve(deleted);
    tx.onerror = () => reject(tx.error);
  });
}

/**
 * Clear all entries from the store.
 */
export async function clear() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readwrite');
    tx.objectStore(config.diagStoreName).clear();
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error || new Error('Transaction aborted'));
  });
}

/**
 * Iterate all entries via cursor, calling `callback(entry)` for each.
 * Used for streaming export without loading everything into memory.
 * @param {function(Object): void} callback
 * @returns {Promise<void>}
 */
export async function iterateAll(callback) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(config.diagStoreName, 'readonly');
    const req = tx.objectStore(config.diagStoreName).openCursor();
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor) {
        try { callback(cursor.value); } catch (err) { reject(err); return; }
        cursor.continue();
      }
    };
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

/** Reset cached DB promise (for testing or error recovery). */
export function _resetDbPromise() { _dbPromise = null; }
