import axios, { AxiosResponse } from 'axios';

import { AnnouncementPost } from 'interfaces';

import { STATUS_CODES } from '../../../constants';

export type AnnouncementsAPI = {
  msg: string;
  posts: AnnouncementPost[];
};

export type AnnouncementsBody = {
  title: string;
  content: string;
}

export type AddAnnouncementsAPI = {
  msg: string;
}

export function getAnnouncements() {
  return axios({
    method: 'get',
    url: '/api/announcements/v0/',
  })
    .then((response: AxiosResponse<AnnouncementsAPI>) => {
      const { data, status } = response;

      return {
        posts: data.posts,
        statusCode: status,
      };
    })
    .catch((e) => {
      const { response } = e;
      const statusCode = response
        ? response.status || STATUS_CODES.INTERNAL_SERVER_ERROR
        : STATUS_CODES.INTERNAL_SERVER_ERROR;

      return Promise.reject({
        posts: [],
        statusCode,
      });
    });
}

export function addAnnouncements(body: AnnouncementsBody) {
  return axios.post('/api/announcements/v0/',body)
    .then((response: AxiosResponse<AddAnnouncementsAPI>) => {
      const { data, status } = response;

      return {
        msg: data.msg,
        statusCode: status,
      };
    })
    .catch((e) => {
      const { response } = e;
      const statusCode = response
        ? response.status || STATUS_CODES.INTERNAL_SERVER_ERROR
        : STATUS_CODES.INTERNAL_SERVER_ERROR;

      return Promise.reject({
        msg: "",
        statusCode,
      });
    });
}
