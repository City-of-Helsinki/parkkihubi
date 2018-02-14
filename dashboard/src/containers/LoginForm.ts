import { Dispatch } from 'redux';
import { connect } from 'react-redux';

import LoginForm, { Props } from '../components/LoginForm';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

function mapStateToProps(state: RootState): Partial<Props> {
    const { auth } = state;
    return {
        phase: (auth.codeToken) ? 'verification-code' : 'login',
        loginErrorMessage: auth.codeTokenFailure,
        verificationCodeErrorMessage: auth.authTokenFailure,
    };
}

function mapDispatchToProps(dispatch: Dispatch<RootState>): Partial<Props> {
    return {
        onLogin: (username: string, password: string) => {
            dispatch(dispatchers.initiateLogin(username, password));
        },
        onVerificationCodeSubmitted: (code: string) => {
            dispatch(dispatchers.continueLogin(code));
        },
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(LoginForm);
