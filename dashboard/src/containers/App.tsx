import * as React from 'react';
import { connect } from 'react-redux';
import { Container, Row, Col } from 'reactstrap';

import { RootState } from '../types';

import LoginForm from './LoginForm';
import Dashboard from './Dashboard';

interface Props {
    isLoading?: boolean;
    showLoginForm?: boolean;
}

class App extends React.Component<Props> {
  render() {
    if (this.props.isLoading) {
      return null;
    } if (this.props.showLoginForm) {
      return (
        <Container fluid>
          <Row>
            <Col className="login-form"
              xs={{ size: 10, offset: 1 }}
              sm={{ size: 8, offset: 2 }}
              md={{ size: 6, offset: 3 }}
              lg={{ size: 4, offset: 4 }}
            >
                <div className="title-section d-flex align-items-center justify-content-center">
                    <img className="logo" src="parkkihubi.svg" alt=""/>
                    <h1>Parkkihubi</h1>
                </div>
              <LoginForm />
            </Col>
          </Row>
        </Container>
      );
    }
    return (<Dashboard />);
  }
}

const mapStateToProps = (state: RootState): Partial<Props> => ({
  isLoading: !state.auth.existingLoginChecked,
  showLoginForm: !state.auth.loggedIn,
});

const ConnectedApp = connect(
  mapStateToProps, null)(App);

export default ConnectedApp;
