import * as React from 'react';
import { connect } from 'react-redux';

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
            return (<LoginForm/>);
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
