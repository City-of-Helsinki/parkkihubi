import { Dispatch } from 'redux';
import moment from 'moment';

import * as actions from './actions';
import { Action } from './actions';
import api from './api';
import { MapViewport } from './components/types';
import { RootState } from './types';

const updateInterval = 5 * 60 * 1000;  // 5 minutes in ms

export function checkExistingLogin() {
  return (dispatch: Dispatch<Action>) => {
    dispatch(actions.checkExistingLogin());
    api.auth.checkExistingLogin().then(
        (authToken) => {
          if (authToken) {
            dispatch(actions.receiveAuthToken(authToken.token));
          }
          dispatch(actions.resolveExistingLoginCheck());
        },
        (error) => {
          dispatch(actions.resolveExistingLoginCheck());
          throw error;
        });
  };
}

export function initiateLogin(username: string, password: string) {
  return (dispatch: Dispatch<Action>) => {
    dispatch(actions.requestCodeToken());
    api.auth.initiateLogin(username, password).then(
        (codeToken) => {
          dispatch(actions.receiveCodeToken(codeToken.token));
        },
        (error) => {
          dispatch(actions.receiveCodeTokenFailure(
              `${error.response.statusText} `
              + `-- ${JSON.stringify(error.response.data)}`));
        });
  };
}

export function continueLogin(verificationCode: string) {
  return (dispatch: Dispatch<Action>, getState: () => RootState) => {
    dispatch(actions.requestAuthToken());
    const { codeToken } = getState().auth;
    if (codeToken) {
      api.auth.continueLogin(codeToken, verificationCode).then(
          (authToken) => {
            dispatch(actions.receiveAuthToken(authToken.token));
          },
          (error) => {
            dispatch(actions.receiveAuthTokenFailure(
                `${error.response.statusText} `
                + `-- ${JSON.stringify(error.response.data)}`));
          });
    }
  };
}

export function logout() {
  return (dispatch: Dispatch<Action>) => {
    api.auth.logout();
    dispatch(actions.logout());
  };
}

export function setMapViewport(viewport: MapViewport) {
  return (dispatch: Dispatch<Action>) => {
    dispatch(actions.setMapViewport(viewport));
  };
}

export function updateData() {
  return (dispatch: Dispatch<any>) => {
    dispatch(setDataTime(moment()));
  };
}

export function setDataTime(time?: moment.Moment) {
  return (dispatch: Dispatch<any>, getState: () => RootState) => {
    if (time && typeof time === 'object' && time.isValid()) {
      const {dataTime} = getState();
      const roundedTime = roundTime(time, updateInterval);
      if (!dataTime || roundedTime.valueOf() !== dataTime) {
        dispatch(actions.setDataTime(roundedTime));
        dispatch(fetchMissingData(roundedTime));
      }
    }
  };
}

function fetchMissingData(time: moment.Moment) {
  return (dispatch: Dispatch<any>, getState: () => RootState) => {
    const timestamp = time.valueOf();
    const state: RootState = getState();
    if (!(timestamp in state.regionUsageHistory)) {
      dispatch(fetchRegionStats(time));
    }
    if (!(timestamp in state.validParkingsHistory)) {
      dispatch(fetchValidParkings(time));
    }
  };
}

function roundTime(time: moment.Moment, precision: number): moment.Moment {
  return moment(Math.floor(time.valueOf() / precision) * precision);
}

export function setAutoUpdate(value: boolean) {
  return (dispatch: Dispatch<Action>) => {
    dispatch(actions.setAutoUpdate(value));
  };
}

export function setSelectedRegion(regionId: string|null) {
  return (dispatch: Dispatch<Action>) => {
    dispatch(actions.setSelectedRegion(regionId));
  };
}

export function fetchRegionStats(time: moment.Moment) {
  return (dispatch: Dispatch<any>, getState: () => RootState) => {
    const {regions} = getState();
    api.fetchRegionStats(
        time,
        (response) => {
          const results = response.data.results || [];
          const needsRegion = results.some(
              (x: {id: string}) => (!(x.id in regions)));
          if (needsRegion) {
            dispatch(fetchRegions());
          }
          dispatch(actions.receiveRegionStats(response.data, time));
        },
        (error) => {
          alert('Region statistics fetch failed: ' + error);
        });
  };
}

export function fetchRegions() {
  return (dispatch: Dispatch<Action>) => {
    api.fetchRegions(
        (response) => {
          dispatch(actions.receiveRegionInfo(response.data));
        },
        (error) => {
          alert('Region fetch failed: ' + error);
        });
  };
}

export function fetchValidParkings(time: moment.Moment) {
  return (dispatch: Dispatch<Action>) => {
    api.fetchValidParkings(
        time,
        (response) => {
          dispatch(actions.receiveValidParkings(response.data, time));
        },
        (error) => {
          alert('Valid parkings fetch failed: ' + error);
        });
  };
}
