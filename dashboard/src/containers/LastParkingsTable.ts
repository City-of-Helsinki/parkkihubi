import moment from 'moment';
import { connect } from 'react-redux';
import BootstrapTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';


import { Parking, ParkingProperties, RootState } from '../types';
import './LastParkingsTable.css'

interface ParkingData extends ParkingProperties {
    id: string;
}

const getDataOfParking = (parking?: Parking): ParkingData|undefined => {
    return (parking) ? {
        id: parking.id,
        ...parking.properties,
    } : undefined;
}

const formatTime  = (timeStamp?: number|null): string =>
    !timeStamp ? '' : moment(timeStamp).format('DD.MM.YYYY HH:mm');

const mapStateToProps = (state: RootState) => {
    const {dataTime, parkings, selectedRegion, validParkingsHistory} = state;
    const validParkings = validParkingsHistory[dataTime || 0] || [];

    const data = validParkings.map(
        (parkingId: string) => getDataOfParking(parkings[parkingId])).filter(
            (d?: ParkingData) =>
                (d && (!selectedRegion || d.region === selectedRegion)));
    const columns = [
        {
            attrs:  { 'data-title': 'Rekisterinumero' },
            text: 'Rekisterinumero',
            dataField: 'registrationNumber',
        }, {
            attrs:  { 'data-title': 'Operaattori' },
            text: 'Operaattori',
            dataField: 'operatorName',
        }, {
            attrs:  { 'data-title': 'Maksuvyöhyke' },
            text: 'Maksuvyöhyke',
            dataField: 'zone',
        }, {
            attrs:  { 'data-title': 'Lippuautomaatin numero' },
            text: 'Lippuautomaatin numero',
            dataField: 'terminalNumber',
            headerStyle: { width: '200px' },
        }, {
            attrs:  { 'data-title': 'Aloitusaika' },
            text: 'Aloitusaika',
            dataField: 'timeStart',
            formatter: formatTime,
        }, {
            attrs:  { 'data-title': 'Loppumisaika' },
            text: 'Loppumisaika',
            dataField: 'timeEnd',
            formatter: formatTime,
        }, {
            attrs:  { 'data-title': 'Luotu' },
            text: 'Luotu',
            dataField: 'createdAt',
            formatter: formatTime,
        }, {
            attrs:  { 'data-title': 'Päivitetty' },
            text: 'Päivitetty',
            dataField: 'modifiedAt',
            formatter: formatTime,
        },
    ];

    const pagination = paginationFactory({
        sizePerPageList: [],
        sizePerPage: 17,
        page: 1,
        showTotal: true,
    });

    return {data, columns, keyField: 'id', bordered: false, pagination};
}

export default connect(mapStateToProps)(BootstrapTable);

