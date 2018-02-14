import { Dispatch } from 'redux';
import * as React from 'react';
import { connect } from 'react-redux';

import { Bar } from 'react-chartjs-2';
import {
    Button, Card, CardHeader, CardBody,
    Container, Row, Col } from 'reactstrap';

import * as dispatchers from '../dispatchers';
import { RootState } from '../types';
import ParkingRegionsMap from './ParkingRegionsMap';
import TimeSelect from './TimeSelect';
import RegionSelector from  './RegionSelector';

import ReactTable from 'react-table';
import 'react-table/react-table.css';

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

        const data = [
            {
                'id': '49df2003-ffac-4cf9-82d4-ef152bb0f539',
                'operator': 'Lippuautomaatit',
                'zone': 1,
                'area': 'Parking Area 3526',
                'terminal': 620,
                'start': '2.5.2018 14:18:05',
                'end': '2.5.2018, 15:48:05',
                'regnum': 'ABC-123',
                'created': '2.5.2018 14:18:12',
                'modified': '2.5.2018 14:18:12',
            },
            {
                'id': 'c0e45595-aecd-4c83-b80e-6940dcfee667',
                'operator': 'Lippuautomaatit',
                'zone': 2,
                'area': 'Parking Area 4012',
                'terminal': 120,
                'start': '2.5.2018 14:08:35',
                'end': '2.5.2018, 14:28:35',
                'regnum': 'CBA-456',
                'created': '2.5.2018 14:08:42',
                'modified': '2.5.2018 14:08:42',
            },
            {
                'id': 'b68d7e75-c4d9-49e1-9767-7816b7a24b13',
                'operator': 'EasyPark',
                'zone': 1,
                'area': '-',
                'terminal': undefined,
                'start': '2.5.2018 14:02:55',
                'end': '2.5.2018, 16:32:55',
                'regnum': 'XYZ-987',
                'created': '2.5.2018 14:02:59',
                'modified': '2.5.2018 14:03:05',
            },
            {
                'id': '051dabe8-ae2e-459f-97fe-cde4daf2de3b',
                'operator': 'Lippuautomaatit',
                'zone': 1,
                'area': 'Parking Area 2359',
                'terminal': 95,
                'start': '2.5.2018 14:01:22',
                'end': '2.5.2018, 14:21:22',
                'regnum': 'KKK-333',
                'created': '2.5.2018 14:01:23',
                'modified': '2.5.2018 14:01:23',
            },
            {
                'id': 'e8cd6df7-11d4-4fa2-9343-33450dd29e48',
                'operator': 'Witrafi',
                'zone': 2,
                'area': 'Parking Area 3374',
                'terminal': undefined,
                'start': '2.5.2018 13:59:45',
                'end': '2.5.2018, 15:28:06',
                'regnum': 'ABC-123',
                'created': '2.5.2018 13:59:46',
                'modified': '2.5.2018 15:28:07',
            },
            {
                'id': '78fff1e1-9a76-4870-8637-be32561b6aed',
                'operator': 'ParkMan',
                'zone': 3,
                'area': '-',
                'terminal': undefined,
                'start': '2.5.2018 13:59:32',
                'end': '2.5.2018, 14:38:35',
                'regnum': 'ZZZ-444',
                'created': '2.5.2018 13:59:32',
                'modified': '2.5.2018 14:38:36',
            },
        ];

        const columns = [
            {
                Header: 'Tunniste',
                accessor: 'id',
            }, {
                Header: 'Rekisterinumero',
                accessor: 'regnum',
            }, {
                Header: 'Operaattori',
                accessor: 'operator',
            }, {
                Header: 'Maksuvyöhyke',
                accessor: 'zone',
            }, {
                Header: 'Pysäköintialue',
                accessor: 'area',
            }, {
                Header: 'Lippuautomaatin numero',
                accessor: 'terminal',
            }, {
                Header: 'Aloitusaika',
                accessor: 'start',
            }, {
                Header: 'Loppumisaika',
                accessor: 'end',
            }, {
                Header: 'Luotu',
                accessor: 'created',
            }, {
                Header: 'Päivitetty',
                accessor: 'modified',
            },
        ];

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
                                <CardHeader>Viimeiset pysäköinnit</CardHeader>
                                <CardBody>
                                    <ReactTable data={data} columns={columns} />
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
