import { Component } from 'react';
import { connect } from 'react-redux';

import { Button } from 'reactstrap';

import RegionSelector from './RegionSelector';
import * as dispatchers from '../dispatchers';
import { RootState } from '../types';

import './Dashboard.css';
import TimeSelect from '../containers/TimeSelect';
import ParkingRegionsMap from './ParkingRegionsMap';
import LastParkingsTable from './LastParkingsTable';

interface Props {
    autoUpdate?: boolean;
    onUpdate?: () => void;
    onLogout?: () => void;
}


class Dashboard extends Component<Props> {
    timer: NodeJS.Timeout|null = null;

    timerInterval: number = 1000; // 1 second

    componentDidMount() {
      if (this.props.autoUpdate && !this.timer) {
        this.enableAutoUpdate();
      }
    }

    // eslint-disable-next-line camelcase
    UNSAFE_componentWillReceiveProps(nextProps: Props) {
      if (nextProps.autoUpdate && !this.timer) {
        this.enableAutoUpdate();
      }
      if (!nextProps.autoUpdate && this.timer) {
        this.disableAutoUpdate();
      }
    }

    enableAutoUpdate = () => {
      if (this.timer) {
        return; // Was already enabled
      }
      this.timer = setInterval(this.autoUpdate, this.timerInterval);
    }

    disableAutoUpdate = () => {
      if (!this.timer) {
        return; // Was already disabled
      }
      clearInterval(this.timer);
      this.timer = null;
    }

    autoUpdate = () => {
      if (this.props.onUpdate) {
        this.props.onUpdate();
      }
    }

    render() {
      return (
        <main className="main d-flex flex-column">
            <div className="toolbar margin-bottom-8">
              <div className="d-flex align-items-center justify-content-center">
                  <img className="logo mini" src="parkkihubi.svg" alt=""/>
                  <h2>Parkkihubi</h2>
              </div>
              <Button
                  className="submit-button d-flex align-items-center"
                  onClick={this.props.onLogout}
                  color="danger"
              >
                  <span>Kirjaudu ulos</span>
                  <i className="fa fa-sign-out" />
              </Button>
            </div>
            <h4>Aktiiviset pysäköinnit</h4>
            <div className="d-flex">
                <div className="table-card">
                    <TimeSelect />
                    <div className="margin-bottom-8" />
                    <LastParkingsTable />
                </div>

                <div style={{width: '16px'}}/>

                <div className="map-card">
                    <RegionSelector />
                    <div className="margin-bottom-8" />
                    <ParkingRegionsMap/>
                </div>
            </div>
        </main>
      );
    }
}

const mapStateToProps = (state: RootState): Props => ({
  autoUpdate: state.autoUpdate,
});

const mapDispatchToProps = (dispatch: any): Props => ({
  onUpdate: () => dispatch(dispatchers.updateData()),
  onLogout: () => dispatch(dispatchers.logout()),
});

export default connect(mapStateToProps, mapDispatchToProps)(Dashboard);
