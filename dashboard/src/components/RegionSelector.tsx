import * as React from 'react';
import Select from 'react-select';

import './RegionSelector.css';

type RegionId = string;
type RegionTuple = [RegionId, string];  // id, name

interface Item {
    value: RegionId;
    label: string;
}

export interface Props {
    regions: RegionTuple[];
    selectedRegion?: RegionId;
    onRegionChanged?: (regionId: RegionId|null, name: string|null) => void;
}

class RegionSelect extends Select<RegionId> {
}

export default class RegionSelector extends React.Component<Props> {
    render() {
        const options = this.props.regions.map(([id, name]) => {
            return {value: id, label: name};
        });
        return (
            <RegionSelect
                className="region-selector"
                value={this.props.selectedRegion}
                options={options}
                onChange={this.handleItemChange}
                placeholder="Valitse alue..."
            />);
    }

    private handleItemChange = (item: Item) => {
        if (this.props.onRegionChanged) {
            if (item) {
                this.props.onRegionChanged(item.value, item.label);
            } else {
                this.props.onRegionChanged(null, null);
            }
        }
    }
}
