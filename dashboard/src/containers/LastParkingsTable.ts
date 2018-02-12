import * as moment from 'moment';
import { connect } from 'react-redux';
import ReactTable, { TableProps } from 'react-table';

import 'react-table/react-table.css';

import { Parking, ParkingProperties, RootState } from '../types';

interface ParkingData extends ParkingProperties {
    id: string;
}

function getDataOfParking(parking?: Parking): ParkingData|undefined {
    return (parking) ? {
        id: parking.id,
        ...parking.properties,
    } : undefined;
}

function formatTime(timestamp?: number|null): string|undefined {
    if (!timestamp) {
        return undefined;
    }
    return moment(timestamp).format('L LTS');
}

function mapStateToProps(state: RootState): Partial<TableProps> {
    const {dataTime, parkings, selectedRegion, validParkingsHistory} = state;
    const validParkings = validParkingsHistory[dataTime || 0] || [];

    const data = validParkings.map(
        (parkingId: string) => getDataOfParking(parkings[parkingId])).filter(
            (d?: ParkingData) =>
                (d && (!selectedRegion || d.region === selectedRegion)));

    const columns = [
        {
            Header: 'Tunniste',
            accessor: 'id',
        }, {
            Header: 'Rekisterinumero',
            accessor: 'registrationNumber',
        }, {
            Header: 'Operaattori',
            accessor: 'operatorName',
        }, {
            Header: 'Maksuvyöhyke',
            accessor: 'zone',
        }, {
            Header: 'Lippuautomaatin numero',
            accessor: 'terminalNumber',
        }, {
            Header: 'Aloitusaika',
            id: 'timeStart',
            accessor: (d: ParkingData) => formatTime(d.timeStart),
        }, {
            Header: 'Loppumisaika',
            id: 'timeEnd',
            accessor: (d: ParkingData) => formatTime(d.timeEnd),
        }, {
            Header: 'Luotu',
            id: 'createdAt',
            accessor: (d: ParkingData) => formatTime(d.createdAt),
        }, {
            Header: 'Päivitetty',
            id: 'modifiedAt',
            accessor: (d: ParkingData) => formatTime(d.modifiedAt),
        },
    ];

    return {data, columns};
}

const mapDispatchToProps = null;

const LastParkingsTable = connect(
    mapStateToProps, mapDispatchToProps)(ReactTable);

export default LastParkingsTable;
