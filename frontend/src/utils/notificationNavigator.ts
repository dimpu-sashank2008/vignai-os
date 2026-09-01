/**
 * VIGNAI OS - Centralized Notification Target Resolver & Navigator
 * 
 * Maps structured notification metadata to exact page routes, section tabs,
 * deep-link anchors, and spotlight elements.
 * 
 * Rules:
 * 1. Do NOT determine navigation by scraping free text if structured fields exist.
 * 2. Role security: Block cross-role routing (e.g. student accessing /management/*).
 * 3. Informational notifications (e.g. password changed) are non-actionable; no fake routes.
 * 4. Mark-read failure MUST NOT block navigation.
 * 5. Reuses existing triggerSpotlight utility.
 */

import { NavigateFunction } from 'react-router-dom';
import { Notification } from '../types';
import { triggerSpotlight } from './searchDeepLink';
import client from '../api/client';

export interface ResolvedNotificationTarget {
  route: string;
  anchor?: string;
  entityType?: string;
  entityId?: string;
  query?: string;
  spotlightId?: string;
  isActionable: boolean;
  isValidRole: boolean;
  state?: Record<string, any>;
  errorReason?: string;
}

/**
 * Validates if the target route is authorized for the given user role.
 */
export function isRouteAuthorizedForRole(route: string, userRole?: string): boolean {
  if (!userRole) return false;
  const role = userRole.toLowerCase();

  const normalized = route.toLowerCase().trim();

  // Management / Admin role check
  if (normalized.startsWith('/management') || normalized.startsWith('/admin')) {
    return role === 'management' || role === 'admin';
  }

  // Faculty role check
  if (normalized.startsWith('/faculty')) {
    return role === 'faculty' || role === 'admin';
  }

  // Student role check
  if (normalized.startsWith('/student')) {
    return role === 'student' || role === 'admin';
  }

  // Public / general shared routes
  return true;
}

/**
 * Resolves a Notification object into a complete, structured navigation target.
 */
export function resolveNotificationTarget(
  notification: Notification,
  userRole?: string
): ResolvedNotificationTarget {
  const normRole = (userRole || 'student').toLowerCase();
  const notifType = (notification.notification_type || '').toUpperCase();

  // Check if notification is purely informational
  if (
    notifType === 'INFORMATIONAL' ||
    (!notification.target_route &&
      !notification.target_entity_type &&
      !notification.source_action_id &&
      !notification.source_alert_id &&
      !notification.source_insight_id &&
      notification.title.toLowerCase().includes('password'))
  ) {
    return {
      route: '',
      isActionable: false,
      isValidRole: true,
    };
  }

  let rawRoute = notification.target_route || '';
  let anchor = notification.target_anchor || '';
  let query = notification.target_query || '';
  const entityType = (notification.target_entity_type || notifType || 'GENERAL').toUpperCase();
  const entityId = notification.target_entity_id || '';
  let spotlightId = anchor || '';
  const state: Record<string, any> = {};

  // Extract anchor or query if embedded in target_route
  if (rawRoute.includes('#')) {
    const parts = rawRoute.split('#');
    rawRoute = parts[0];
    if (!anchor) anchor = parts[1];
  }
  if (rawRoute.includes('?')) {
    const parts = rawRoute.split('?');
    rawRoute = parts[0];
    if (!query) query = parts[1];
  }

  // Fallback route deduction based on entityType and user role if target_route is missing
  if (!rawRoute) {
    switch (entityType) {
      case 'ACADEMIC':
        rawRoute = '/student/academics';
        anchor = anchor || (entityId ? `attendance-${entityId.toLowerCase()}` : 'attendance');
        break;
      case 'CAREER':
        rawRoute = '/student/career';
        anchor = anchor || (entityId ? `opportunity-${entityId}` : 'opportunities');
        break;
      case 'CASE':
      case 'COMPLAINT':
        if (normRole === 'faculty') {
          rawRoute = entityId ? `/faculty/cases/${entityId}` : '/faculty/cases';
        } else if (normRole === 'management' || normRole === 'admin') {
          rawRoute = entityId ? `/management/cases/${entityId}` : '/management/issues';
        } else {
          rawRoute = '/student/complaints';
          anchor = anchor || (entityId ? `case-${entityId}` : 'complaints-list');
        }
        break;
      case 'CASE_GROUP':
      case 'ALERT':
        if (normRole === 'management' || normRole === 'admin') {
          rawRoute = '/management/issues';
          anchor = anchor || (entityId ? `group-${entityId}` : 'campus-issues');
        } else {
          rawRoute = '/faculty/cases';
          anchor = anchor || (entityId ? `group-${entityId}` : 'faculty-cases-queue');
        }
        break;
      case 'ACTION':
        rawRoute = `/${normRole}`;
        anchor = anchor || (notification.source_action_id ? `action-${notification.source_action_id}` : 'vignai-action-center');
        break;
      case 'WHAT_IF':
        rawRoute = '/management/what-if';
        anchor = 'what-if-lab';
        break;
      case 'PROFILE':
        rawRoute = `/${normRole}/profile`;
        break;
      default:
        // Informational or untargeted notification
        return {
          route: '',
          isActionable: false,
          isValidRole: true,
        };
    }
  }

  // Ensure spotlight ID matches anchor or entity
  if (!spotlightId) {
    if (anchor) {
      spotlightId = anchor;
    } else if (entityId) {
      if (entityType === 'CAREER') spotlightId = `opportunity-${entityId}`;
      else if (entityType === 'ACADEMIC') spotlightId = `attendance-${entityId.toLowerCase()}`;
      else if (entityType === 'CASE' || entityType === 'COMPLAINT') spotlightId = `case-${entityId}`;
      else if (entityType === 'CASE_GROUP') spotlightId = `group-${entityId}`;
      else if (entityType === 'ACTION') spotlightId = `action-${entityId}`;
    }
  }

  // Configure role-aware tab states for destination views
  if (rawRoute.startsWith('/student/academics')) {
    state.activeTab = anchor?.includes('assessment') || anchor?.includes('marks') ? 'ASSESSMENTS' : 'ATTENDANCE';
    if (entityId) state.subjectCode = entityId;
  } else if (rawRoute.startsWith('/student/career')) {
    state.activeTab = anchor?.includes('skill') ? 'SKILL_GAPS' : 'OPPORTUNITIES';
    if (entityId) state.opportunityId = entityId;
  } else if (rawRoute.startsWith('/management/what-if') || rawRoute.startsWith('/management/simulations')) {
    state.activeTab = 'LAB';
  }

  state.targetId = spotlightId;

  // Validate role authorization
  const isValidRole = isRouteAuthorizedForRole(rawRoute, userRole);
  if (!isValidRole) {
    return {
      route: rawRoute,
      anchor,
      query,
      entityType,
      entityId,
      spotlightId,
      isActionable: true,
      isValidRole: false,
      errorReason: 'UNAUTHORIZED_ROLE',
    };
  }

  return {
    route: rawRoute,
    anchor,
    query,
    entityType,
    entityId,
    spotlightId,
    isActionable: true,
    isValidRole: true,
    state,
  };
}

/**
 * Handles notification click event:
 * 1. Marks notification as read (failures do not block navigation).
 * 2. Resolves structured destination target.
 * 3. Validates role authorization.
 * 4. Navigates to target route with state.
 * 5. Triggers spotlight highlight on DOM target element.
 */
export async function navigateNotification(
  notification: Notification,
  navigate: NavigateFunction,
  userRole?: string,
  showToast?: (message: string, type?: 'info' | 'success' | 'error') => void,
  onMarkReadSuccess?: (id: number) => void
): Promise<void> {
  // 1. Mark as read immediately (mark-read failure must not block navigation)
  if (!notification.is_read) {
    try {
      await client.post(`/notifications/${notification.id}/read`);
      if (onMarkReadSuccess) {
        onMarkReadSuccess(notification.id);
      }
    } catch (err) {
      console.warn('VIGNAI: Notification mark as read failed (continuing navigation):', err);
    }
  }

  // 2. Resolve destination
  const target = resolveNotificationTarget(notification, userRole);

  // Purely informational notification: no navigation
  if (!target.isActionable) {
    return;
  }

  // 3. Check role security
  if (!target.isValidRole) {
    if (showToast) {
      showToast('This notification destination cannot be accessed with your current account role.', 'error');
    }
    return;
  }

  // 4. Construct complete URL
  let fullUrl = target.route;
  if (target.query) {
    fullUrl += (fullUrl.includes('?') ? '&' : '?') + target.query;
  }
  if (target.anchor) {
    fullUrl += `#${target.anchor}`;
  }

  // 5. Navigate with target state
  navigate(fullUrl, { state: target.state });

  // 6. Trigger spotlight highlighting
  if (target.spotlightId) {
    setTimeout(() => {
      triggerSpotlight(target.spotlightId!, 3500, 4000);
    }, 150);
  }
}
