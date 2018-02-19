import * as React from 'react';
import { connect } from 'react-redux';
import { Container, Row, Col } from 'reactstrap';

import { RootState } from '../types';

import Dashboard from './Dashboard';
import LoginForm from './LoginForm';

interface Props {
    isLoading?: boolean;
    showLoginForm?: boolean;
}

class App extends React.Component<Props> {
    render() {
        if (this.props.isLoading) {
            return null;
        } else if (this.props.showLoginForm) {
            return (
                <Container fluid={true}>
                    <Row>
                        <Col
                            xs={{size: 10, offset: 1}}
                            sm={{size: 8, offset: 2}}
                            md={{size: 6, offset: 3}}
                            lg={{size: 4, offset: 4}}
                        >
                            <LoginForm/>
                        </Col>
                    </Row>
                </Container>
            );
        } else {
            return (<Dashboard/>);
        }
    }
}

function mapStateToProps(state: RootState): Partial<Props> {
    return {
        isLoading: !state.auth.existingLoginChecked,
        showLoginForm: !state.auth.loggedIn,
    };
}

const mapDispatchToProps = null;

const ConnectedApp = connect(
    mapStateToProps, mapDispatchToProps)(App);

export default ConnectedApp;
