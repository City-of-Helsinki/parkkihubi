import { connect } from 'react-redux';

import LoginForm, { Props } from '../components/LoginForm';
import { RootState } from '../types';
import * as dispatcher from '../dispatchers';

const mapStateToProps = (state: RootState): Partial<Props> => ({
  phase: (state.auth.codeToken) ? 'verification-code' : 'login',
  loginErrorMessage: state.auth.codeTokenFailure,
  verificationCodeErrorMessage: state.auth.authTokenFailure,
});

const mapDispatchToProps = (dispatch: any): Partial<Props> => ({
  onLogin: (username: string, password: string) => dispatch(dispatcher.initiateLogin(username, password)),
  onVerificationCodeSubmitted: (code: string) => dispatch(dispatcher.continueLogin(code)),
});

export default connect(mapStateToProps, mapDispatchToProps)(LoginForm);
