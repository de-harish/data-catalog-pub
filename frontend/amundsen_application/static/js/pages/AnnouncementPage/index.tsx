// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
// TODO - Consider an alternative to react-sanitized-html (large filesize)
import SanitizedHTML from 'react-sanitized-html';

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import { GlobalState } from 'ducks/rootReducer';
import { AddAnnouncementsRequest, GetAnnouncementsRequest } from 'ducks/announcements/types';
import { getAnnouncements } from 'ducks/announcements';
import { addAnnouncements } from 'ducks/announcements/api/v0';
import { AnnouncementPost } from 'interfaces';

const ANNOUNCEMENTS_HEADER_TEXT = 'Announcements';

export interface StateFromProps {
  posts: AnnouncementPost[];
}

export interface DispatchFromProps {
  announcementsGet: () => GetAnnouncementsRequest;
}

export type AnnouncementPageProps = StateFromProps & DispatchFromProps;
interface AnnouncementPageState {
  title: string;
  content: string;
}

export class AnnouncementPage extends React.Component<AnnouncementPageProps,AnnouncementPageState> {

  constructor(props) {
    super(props);

    this.state = {
      title: "",
      content: ""
    }
  }

componentDidMount() {
  const { announcementsGet } = this.props;

  announcementsGet();
}

createAnnouncement = async () => {
  const body = {
    title: this.state.title,
    content: this.state.content
  }
  await addAnnouncements(body)
  this.setState({
    title:"",
    content: ""
  })
  this.props.announcementsGet();
}

displayPost(post: AnnouncementPost, postIndex: number) {
  return (
    <div key={`post:${postIndex}`} className="post-container">
      <div className="post-header">
        <h2 className="post-title title-2">{post.title}</h2>
        <div className="body-secondary-3">{post.date}</div>
      </div>
      <div className="post-content">
        <SanitizedHTML html={post.html_content} />
      </div>
    </div>
  );
}

displayPosts() {
  const { posts } = this.props;

  return posts.map((post, index) => this.displayPost(post, index));
}

render() {
  return (
    <DocumentTitle title="Announcements - Amundsen">
      <main className="container announcement-container">
        <div className="row">
          <div className="col-xs-12 col-md-10 col-md-offset-1">
            <h1 id="announcement-header" className="announcement-header">
              {ANNOUNCEMENTS_HEADER_TEXT}
            </h1>
            <hr />
            <div className="create-announcement">
              <h2>Create Announcement</h2>
              <label style={{marginRight: 12}}>Title</label>
              <input value={this.state.title} onChange={(e) => {
                this.setState({
                  title: e.target.value
                })
              }} />
              <label style={{marginRight: 12}}>Content</label>
              <textarea value={this.state.content} onChange={(e) => {
                this.setState({
                  content: e.target.value
                })
              }} />
              <button className="announcements-button" onClick={this.createAnnouncement}>Create Announcement</button>
            </div>
            <div id="announcement-content" className="announcement-content">
              {this.displayPosts()}
            </div>
          </div>
        </div>
      </main>
    </DocumentTitle>
  );
}
}

export const mapStateToProps = (state: GlobalState) => ({
  posts: state.announcements.posts,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ announcementsGet: getAnnouncements }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(AnnouncementPage);
