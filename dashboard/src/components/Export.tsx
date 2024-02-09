import DateTime from "react-datetime";
import Select from "react-select";
import moment, { Moment } from "moment";
import { Component } from "react";
import { Button } from "reactstrap";
import { ExportFilters } from "../api/types";
import { Operators, PaymentZones } from "../types";

import "./Export.css";

type Option = {
    value: string;
    label: string;
};

interface State {
    operatorSelections: string[];
    paymentZoneSelections: string[];
    startTime: Moment;
    endTime: Moment;
    parking_check: boolean;
    showOptions: boolean;
}

export interface Props {
    operators: Operators,
    paymentZones: PaymentZones,
    downloadCSV?: (filters: ExportFilters) => void;
}

const initialState: State = {
    showOptions: false,
    operatorSelections: [],
    paymentZoneSelections: [],
    startTime: moment().subtract(30, 'days'),
    endTime: moment(),
    parking_check: false,
}

class Export extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = initialState;
    }

    handleExportButtonClick = () => {
        this.setState((prevState) => ({...initialState, showOptions: !prevState.showOptions}));
    }

    handleDownloadClick = () => {
        if (this.props.downloadCSV) {
            const filters: ExportFilters = {
                ...(this.state.operatorSelections.length && { operators: this.state.operatorSelections }),
                ...(this.state.paymentZoneSelections.length && { payment_zones: this.state.paymentZoneSelections }),
                time_start: this.state.startTime.format("DD.MM.YYYY HH.mm"),
                time_end: this.state.endTime.format("DD.MM.YYYY HH.mm"),
                parking_check: this.state.parking_check,
            };

            this.props.downloadCSV(filters);
        }
    };

    handleDateChange = (time: moment.Moment | string, name: string) => {
        this.setState({
            [name]: moment(time)
        } as any);
    };

    handleOperatorSelect = (options: Option[]) => {
        this.setState({
            operatorSelections: options.map((option) => option.value),
        });
    };

    handlePaymentZoneSelect = (options: Option[]) => {
        this.setState({
            paymentZoneSelections: options.map((option) => option.value),
        });
    };

    handleCheckParkingCheckBoxChange = () => {
        this.setState((prevState) => ({
            parking_check: !prevState.parking_check,
        }));
    };

    render() {
        const {
            operators,
            paymentZones
        } = this.props;
        const operatorOptions = Object.keys(operators).map((k) => ({value: operators[k].id, label: operators[k].name}));
        const paymentZoneOptions = Object.keys(paymentZones).map((k) => ({value: paymentZones[k].code, label: paymentZones[k].name}));

        return (
            <>
                <Button
                    className="export-button"
                    color="info"
                    outline={true}
                    onClick={this.handleExportButtonClick}
                >
                    <i className="fa fa-share"></i>
                    <span className="text">Vie</span>
                </Button>
                {this.state.showOptions === true ? (
                    <div className="filter-card">
                        <div className="row">
                            <Select
                                isMulti={true}
                                options={operatorOptions}
                                className="filter-field multi-select-field"
                                onChange={(option) =>
                                    this.handleOperatorSelect(option as Option[])
                                }
                                placeholder="Valitse operaattori"
                            />
                            <Select
                                isMulti={true}
                                options={paymentZoneOptions}
                                className="filter-field multi-select-field"
                                onChange={(option) =>
                                    this.handlePaymentZoneSelect(option as Option[])
                                }
                                placeholder="Valitse maksuvyöhyke"
                            />
                        </div>
                        <div className="row">
                            <DateTime
                                dateFormat="DD.MM.YYYY"
                                timeFormat="HH.mm"
                                className="filter-field datepicker-field"
                                onChange={(moment) =>
                                    this.handleDateChange(moment, "startTime")
                                }
                                initialValue={this.state.startTime}
                                inputProps={{readOnly: true}}
                            />
                            <DateTime
                                dateFormat="DD.MM.YYYY"
                                timeFormat="HH.mm"
                                className="filter-field datepicker-field"
                                onChange={(moment) =>
                                    this.handleDateChange(moment, "endTime")
                                }
                                initialValue={this.state.endTime}
                                inputProps={{readOnly: true}}
                            />
                            <Button
                                className={
                                    this.state.parking_check === true 
                                    ? "filter-field parking-check-button parking-check-active"
                                    : "filter-field parking-check-button"
                                }
                                color="info"
                                outline={true}
                                onClick={this.handleCheckParkingCheckBoxChange}
                            >
                                <i className="fa fa-check-circle" />
                                <span className="text">Tarkistettu</span>
                            </Button>
                            <Button
                                className="filter-field download-button"
                                color="info"
                                outline={true}
                                onClick={this.handleDownloadClick}
                            >
                                <i className="fa fa-download" />
                                <span className="text">Lataa</span>
                            </Button>
                        </div>
                    </div>
                ) : null}
            </>
        );
    }
}

export default Export;
