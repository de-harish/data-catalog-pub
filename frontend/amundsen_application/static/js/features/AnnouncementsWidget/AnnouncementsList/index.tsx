// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import SanitizedHTML from 'react-sanitized-html';
import * as sanitizeHtml from 'sanitize-html';

import { AnnouncementPost } from 'interfaces';
import { logClick } from 'utils/analytics';
import Card from '../../../components/Card';

import {
  MORE_LINK_TEXT,
  NO_ANNOUNCEMENTS_TEXT,
  ANNOUNCEMENTS_ERROR_TEXT,
  HEADER_TEXT,
} from '../constants';

import './styles.scss';

const ANNOUNCEMENT_LIST_THRESHOLD = 3;
const ANNOUNCEMENTS_PAGE_PATH = '/announcements';

const STATIC_ANNOUNCEMENTS: AnnouncementPost[] = [
  {
    date: "2023-07-17",
    title: "Data catalog is under development.",
    html_content: "<p>Metadata for some tables might be missing. The data governance team is working on it.</p>",
  },
  {
    date: "2023-07-14",
    title: "Data Lineage",
    html_content: "<p>Lineage for tables are with depth level 2. Please check the Table detail page of the level 2 dependencies further.</p>",
  },
  // Add more static announcements here as necessary
];


export interface AnnouncementsListProps {
  announcements: AnnouncementPost[];
  hasError?: boolean;
  isLoading?: boolean;
}

const getLatestsAnnouncements = (announcements: AnnouncementPost[]) =>
  announcements.length > ANNOUNCEMENT_LIST_THRESHOLD
    ? announcements.slice(0, ANNOUNCEMENT_LIST_THRESHOLD)
    : announcements;

const times = (numItems: number) => new Array(numItems).fill(0);

const allowedAttributes = () => {
  const attributes = sanitizeHtml.defaults.allowedAttributes;

  attributes.a.push('onclick');

  return attributes;
};

const AnnouncementItem: React.FC<AnnouncementPost> = ({
  date,
  title,
  html_content,
}: AnnouncementPost) => (
  <li className="announcement">
    <Card
      title={title}
      subtitle={date}
      // href={ANNOUNCEMENTS_PAGE_PATH}
      // onClick={logClick}
      type="announcement-card"
      copy={
        <SanitizedHTML
          className="announcement-content"
          html={html_content}
          allowedAttributes={allowedAttributes()}
        />
      }
    />
  </li>
);

const EmptyAnnouncementItem: React.FC = () => (
  <li className="empty-announcement">{NO_ANNOUNCEMENTS_TEXT}</li>
);
const AnnouncementErrorItem: React.FC = () => (
  <li className="error-announcement">{ANNOUNCEMENTS_ERROR_TEXT}</li>
);

const AnnouncementsList: React.FC<AnnouncementsListProps> = ({
  announcements,
  hasError,
  isLoading,
}: AnnouncementsListProps) => {
  const isEmpty = STATIC_ANNOUNCEMENTS.length === 0;
  let listContent: JSX.Element[] = [];

  console.log('Debug', STATIC_ANNOUNCEMENTS.length)
  if (isEmpty) {
    listContent = [<EmptyAnnouncementItem />];
  }
  if (STATIC_ANNOUNCEMENTS.length > 0) {
    listContent = getLatestsAnnouncements(STATIC_ANNOUNCEMENTS).map(
      ({ date, title, html_content }) => (
        <AnnouncementItem
          key={`key:${date}`}
          date={date}
          title={title}
          html_content={html_content}
        />
      )
    );
  }
  // if (hasError) {
  //   listContent = [<AnnouncementErrorItem />];
  // }
  if (isLoading) {
    listContent = times(3).map((_, index) => (
      <li className="announcement" key={`key:${index}`}>
        <Card isLoading />
      </li>
    ));
  }

  return (
    <article className="announcements-list-container">
      <h2 className="announcements-list-title">{HEADER_TEXT}</h2>
      <ul className="announcements-list">{listContent}</ul>
      {!isEmpty && (
        <Link
          to={ANNOUNCEMENTS_PAGE_PATH}
          className="announcements-list-more-link"
          onClick={logClick}
        >
          {/*{MORE_LINK_TEXT}*/}
        </Link>
      )}
    </article>
  );
};

export default AnnouncementsList;
