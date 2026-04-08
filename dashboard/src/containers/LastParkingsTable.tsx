import moment from 'moment';
import { connect } from 'react-redux';
import DataTable, {
    TableColumn,
    TableStyles,
} from 'react-data-table-component';

import { Parking, ParkingProperties, RootState } from '../types';

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
    !timeStamp ? '' : moment(timeStamp).format('D.M.YYYY HH:mm');

const toParkingData = (
    selectedRegion: string | null,
    parkings: RootState['parkings']
) => (parkingId: string): ParkingData | undefined => {
    const data = getDataOfParking(parkings[parkingId]);
    if (!data) {
        return undefined;
    }
    if (selectedRegion && data.region !== selectedRegion) {
        return undefined;
    }
    return data;
};

const isParkingData = (value: ParkingData | undefined): value is ParkingData =>
    value !== undefined;

const columns: TableColumn<ParkingData>[] = [
    {
        name: 'Rekisterinumero',
        selector: (row) => row.registrationNumber,
        sortable: true,
        minWidth: '12em',
    },
    {
        name: 'Operaattori',
        selector: (row) => row.operatorName,
        sortable: true,
        minWidth: '12em',
    },
    {
        name: 'Maksuvyöhyke',
        selector: (row) => row.zone,
        sortable: true,
        minWidth: '10em',
    },
    {
        name: 'Lippuautomaatti',
        selector: (row) => row.terminalNumber || '',
        sortable: true,
        minWidth: '12em',
    },
    {
        name: 'Aloitusaika',
        selector: (row) => row.timeStart || 0,
        cell: (row) => formatTime(row.timeStart),
        sortable: true,
        minWidth: '10em',
    },
    {
        name: 'Loppumisaika',
        selector: (row) => row.timeEnd || 0,
        cell: (row) => formatTime(row.timeEnd),
        sortable: true,
        minWidth: '10em',
    },
    {
        name: 'Luotu',
        selector: (row) => row.createdAt || 0,
        cell: (row) => formatTime(row.createdAt),
        sortable: true,
        minWidth: '10em',
    },
    {
        name: 'Päivitetty',
        selector: (row) => row.modifiedAt || 0,
        cell: (row) => formatTime(row.modifiedAt),
        sortable: true,
        minWidth: '10em',
    },
];

interface Props {
    data: ParkingData[];
}

const mapStateToProps = (state: RootState) => {
    const {dataTime, parkings, selectedRegion, validParkingsHistory} = state;
    const validParkings = validParkingsHistory[dataTime || 0] || [];

    const data = validParkings
        .map(toParkingData(selectedRegion, parkings))
        .filter(isParkingData);
    return {data};
}

const styles: TableStyles = {
    cells: { style: { fontSize: '90%' } },
    headCells: { style: { backgroundColor: 'var(--bs-primary)' } },
};

const LastParkingsTable = ({ data }: Props) => (
    <DataTable
        columns={columns}
        data={data}
        keyField="id"
        striped={true}
        highlightOnHover={true}
        dense={true}
        pagination={true}
        paginationPerPage={25}
        paginationRowsPerPageOptions={[10, 20, 25, 50, 100]}
        customStyles={styles}
    />
);

export default connect(mapStateToProps)(LastParkingsTable);
