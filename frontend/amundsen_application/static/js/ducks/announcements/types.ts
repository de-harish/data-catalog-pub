import { AnnouncementPost } from 'interfaces';

export enum GetAnnouncements {
  REQUEST = 'amundsen/announcements/GET_REQUEST',
  SUCCESS = 'amundsen/announcements/GET_SUCCESS',
  FAILURE = 'amundsen/announcements/GET_FAILURE',
}

export enum AddAnnouncements {
  REQUEST = 'amundsen/announcements/GET_REQUEST',
  SUCCESS = 'amundsen/announcements/GET_SUCCESS',
  FAILURE = 'amundsen/announcements/GET_FAILURE',
}

export interface GetAnnouncementsRequest {
  type: GetAnnouncements.REQUEST;
}

export interface GetAnnouncementsResponse {
  type: GetAnnouncements.SUCCESS | GetAnnouncements.FAILURE;
  payload: GetAnnouncementsPayload;
}

export interface GetAnnouncementsPayload {
  posts?: AnnouncementPost[];
  statusCode?: number;
}

export interface AddAnnouncementsRequest {
  type: AddAnnouncements.REQUEST;
}

export interface AddAnnouncementsResponse {
  type: AddAnnouncements.SUCCESS | AddAnnouncements.FAILURE;
  payload: AddAnnouncementsPayload;
}

export interface AddAnnouncementsPayload {
  msg: string
}
