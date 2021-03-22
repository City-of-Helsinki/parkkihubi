import * as React from 'react';
import {
  Alert, Button, Form, FormGroup, Label, Input,
} from 'reactstrap';

export interface Props {
    phase?: 'login' | 'verification-code';
    loginErrorMessage?: string;
    verificationCodeErrorMessage?: string;
    onLogin?: (username: string, password: string) => void;
    onVerificationCodeSubmitted?: (code: string) => void;
}

export interface State {
    username: string;
    password: string;
    verificationCode: string;
}

const Field = ({ name, text, ...inputProps }: {
    name: string;
    text: string;
    [key: string]: {};
}) => (
  <FormGroup>
    <Label for={name}>{text}</Label>
    <Input
      type={(name !== 'password') ? 'text' : 'password'}
      name={name}
      id={name}
      {...inputProps}
    />
  </FormGroup>
);

export default class LoginForm extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      verificationCode: '',
    };
  }

  render() {
    return (
      <Form onSubmit={this.handleSubmit}>
        {(this.props.phase === 'login') ? (
          <>
            <Field
              name="username"
              text="Käyttäjätunnus"
              value={this.state.username}
              onChange={this.handleChange}
            />
            <Field
              name="password"
              text="Salasana"
              value={this.state.password}
              onChange={this.handleChange}
            />
            {(this.props.loginErrorMessage) ? (
              <Alert color="danger">{this.props.loginErrorMessage}</Alert>
            ) : null}
          </>
        ) : (
          <>
            <Field
              name="verificationCode"
              text="Varmennuskoodi"
              value={this.state.verificationCode}
              onChange={this.handleChange}
            />
            {(this.props.verificationCodeErrorMessage) ? (
              <Alert color="danger">{this.props.verificationCodeErrorMessage}</Alert>
            ) : null}
          </>
        )}
        <div className="d-flex justify-content-end">
            <Button
                type="submit"
                onClick={this.handleSubmit}
                color="primary"
                className="submit-button d-flex align-items-center"
            >
                {(this.props.phase === 'login') ? (
                    <>
                        <span>Seuraava</span>
                        <i className="fa fa-chevron-right" />
                    </>
                ) : (
                    <>
                        <span>Kirjaudu</span>
                        <i className="fa fa-sign-in" />
                    </>
                )}
            </Button>
        </div>
      </Form>
    );
  }

    private handleChange = (event: React.FormEvent<HTMLInputElement>) => {
      const target = event.target as HTMLInputElement;
      if (target.name === 'username') {
        this.setState({ username: target.value });
      } else if (target.name === 'password') {
        this.setState({ password: target.value });
      } else if (target.name === 'verificationCode') {
        this.setState({ verificationCode: target.value });
      }
    }

    private handleSubmit = (event: React.FormEvent<HTMLElement>) => {
      event.preventDefault();
      const { props, state } = this;
      if (props.phase === 'login' && props.onLogin) {
        props.onLogin(state.username, state.password);
      } else if (props.phase === 'verification-code'
                   && props.onVerificationCodeSubmitted) {
        props.onVerificationCodeSubmitted(state.verificationCode);
      }
      this.setState({ username: '', password: '' });
    }
}
