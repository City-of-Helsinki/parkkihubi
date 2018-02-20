import { Dispatch } from 'redux';
import * as React from 'react';
import { connect } from 'react-redux';

import { Bar } from 'react-chartjs-2';
import {
    Button, Card, CardHeader, CardBody,
    Container, Row, Col } from 'reactstrap';

import * as dispatchers from '../dispatchers';
import { RootState } from '../types';
import LastParkingsTable from './LastParkingsTable';
import ParkingRegionsMap from './ParkingRegionsMap';
import TimeSelect from './TimeSelect';
import RegionSelector from  './RegionSelector';

import './Dashboard.css';

const bar = {
    labels: ['16', '18', '20', '22', '0', '2', '4', '6', '8', '10', '12', '14'],
    datasets: [
        {
            backgroundColor: 'rgba(255,99,132,0.2)',
            borderColor: 'rgba(255,99,132,1)',
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(255,99,132,0.4)',
            hoverBorderColor: 'rgba(255,99,132,1)',
            data: [108, 95, 75, 35, 25, 21, 28, 35, 89, 81, 92, 99]
        }
    ]
};

interface Props {
    autoUpdate: boolean;
    onUpdate: () => void;
    onLogout: (event: React.MouseEvent<{}>) => void;
}

type TimerId = number;

class Dashboard extends React.Component<Props> {
    timer: TimerId|null = null;
    timerInterval: number = 1000; // 1 second

    componentDidMount() {
        if (this.props.autoUpdate && !this.timer) {
            this.enableAutoUpdate();
        }
    }

    componentWillReceiveProps(nextProps: Props) {
        if (nextProps.autoUpdate && !this.timer) {
            this.enableAutoUpdate();
        }
        if (!nextProps.autoUpdate && this.timer) {
            this.disableAutoUpdate();
        }
    }

    enableAutoUpdate() {
        this.autoUpdate();
        if (this.timer) {
            return;  // Was already enabled
        }
        this.timer = window.setInterval(
            this.autoUpdate.bind(this), this.timerInterval);
    }

    disableAutoUpdate() {
        if (!this.timer) {
            return;  // Was already disabled
        }
        window.clearInterval(this.timer);
        this.timer = null;
    }

    autoUpdate() {
        if (this.props.onUpdate) {
            this.props.onUpdate();
        }
    }

    render() {
        return (
            <main className="main">
                <Container fluid={true} className="dashboard">
                    <Row>
                        <Col xl="7" lg="6" md="6" sm="12">
                            <Card>
                                <CardBody>
                                    <TimeSelect/>
                                </CardBody>
                            </Card>
                            <Card className="parking-histogram">
                                <CardHeader>Pysäköintimäärät, viimeiset 24 t</CardHeader>
                                <CardBody>
                                    <Bar
                                        data={bar}
                                        options={{
                                            maintainAspectRatio: false,
                                            legend: {display: false},
                                            scales: {yAxes: [{ticks: {min: 0}}]}
                                        }}
                                    />
                                </CardBody>
                            </Card>
                        </Col>
                        <Col xl="5" lg="6" md="6" sm="12">
                            <Card>
                                <CardBody>
                                    <RegionSelector/>
                                </CardBody>
                            </Card>
                            <Card className="map-card">
                                <CardBody>
                                    <ParkingRegionsMap/>
                                </CardBody>
                            </Card>
                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <Card>
                                <CardHeader>
                                    Aktiiviset pysäköinnit
                                </CardHeader>
                                <CardBody>
                                    <LastParkingsTable/>
                                </CardBody>
                            </Card>
                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <Button
                                onClick={this.props.onLogout}
                                color="danger"
                            >
                                <i className="fa fa-sign-out"/>{' '}Kirjaudu ulos
                            </Button>
                        </Col>
                    </Row>
                </Container>
            </main>
        );
    }
}

function mapStateToProps(state: RootState): Partial<Props> {
    return {
        autoUpdate: state.autoUpdate,
    };
}

function mapDispatchToProps(dispatch: Dispatch<RootState>): Partial<Props> {
    return {
        onUpdate: () => dispatch(dispatchers.updateData()),
        onLogout: (event: React.MouseEvent<{}>) => dispatch(dispatchers.logout()),
    };
}

const ConnectedDashboard = connect(
    mapStateToProps, mapDispatchToProps)(Dashboard);

export default ConnectedDashboard;
