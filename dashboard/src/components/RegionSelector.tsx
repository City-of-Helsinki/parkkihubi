import Select from 'react-select';

import './RegionSelector.css';

type RegionId = string;
type RegionTuple = [RegionId, string]; // id, name

interface Item {
    value: RegionId;
    label: string;
}

export interface Props {
    regions?: RegionTuple[];
    selectedRegion?: RegionId;
    onRegionChanged?: (regionId: RegionId|null, name: string|null) => void;
}

const RegionSelector = (props: Props) => {
    const handleItemChange = (item: Item|null) => {
        if (props.onRegionChanged) {
            if (item) {
                props.onRegionChanged(item.value, item.label);
            } else {
                props.onRegionChanged(null, null);
            }
        }
    }
    const options = props.regions ?
        props.regions.map(([id, name]) => ({ value: id, label: name })) :
        [];
    return (<Select
        className="region-selector"
        value={options.filter(item => item.value === props.selectedRegion)}
        options={options}
        onChange={handleItemChange}
        isClearable={true}
        placeholder="Valitse alue..."
      />);
}
export default RegionSelector;
