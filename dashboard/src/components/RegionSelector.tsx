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
    onRegionChanged?: (regionId: RegionId, name: string) => void;
}

const RegionSelector = (props: Props) => {
    const handleItemChange = (item: Item) => {
        if (props.onRegionChanged) {
            if (item) {
                props.onRegionChanged(item.value, item.label);
            } else {
                props.onRegionChanged(null, null);
            }
        }
    }
    const options = props.regions.map(([id, name]) => ({ value: id, label: name }));
    const defaultValue = options[0];
    return (<Select
        className="region-selector"
        defaultValue={defaultValue}
        options={options}
        onChange={handleItemChange}
        placeholder="Valitse alue..."
      />);
}
export default RegionSelector;
