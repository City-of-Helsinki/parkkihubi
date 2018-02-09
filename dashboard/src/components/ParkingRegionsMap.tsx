import * as chroma from 'chroma-js';
import * as geojson from 'geojson';
import * as Leaflet from 'leaflet';
import * as React from 'react';
import * as ReactLeaflet from 'react-leaflet';

import { MapViewport, Point, Region, RegionProperties } from './types';

import './ParkingRegionsMap.css';

// Add viewport props to the allowed props for Map component, since
// they are missing from the latest libdefs available.
// See https://github.com/DefinitelyTyped/DefinitelyTyped/issues/22125
interface Viewport { center: Point; zoom: number; }
interface MapProps extends ReactLeaflet.MapProps {
    onViewportChange?: (viewport: Viewport) => void;
    onViewportChanged?: (viewport: Viewport) => void;
    viewport?: Viewport;
}
class Map extends ReactLeaflet.Map<MapProps> {}

export interface Props {
    center: Point;
    zoom: number;
    regions?: Region[];
    onRegionClicked?: (region: Region) => void;
    onViewportChanged?: (viewport: MapViewport) => void;
}

export default class ParkingRegionsMap extends React.Component<Props> {
    private map?: ReactLeaflet.Map;

    render() {
        const geoJsonElement = this.props.regions ? (
            <ReactLeaflet.GeoJSON
                key={getKeyForRegions(this.props.regions)}
                data={getFeatureCollection(this.props.regions)}
                style={getStyleForRegion}
                onEachFeature={this.bindPopupToRegion}
            />
        ) : null;
        const osmAttribution = (
            '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>'
            + ' contributors');
        return (
            <Map
                center={this.props.center}
                zoom={this.props.zoom}
                onViewportChanged={this.handleViewportChange}
                ref={(component: ReactLeaflet.Map) => {
                        this.map = component; }}
            >
                <ReactLeaflet.TileLayer
                    url="//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution={osmAttribution}
                />
                <ReactLeaflet.ScaleControl
                    metric={true}
                    imperial={false}
                    maxWidth={150}
                />
                {geoJsonElement}
            </Map>);
    }

    private bindPopupToRegion = (
        region: Region,
        layer: Leaflet.Layer
    ): void => {
        const props = region.properties;
        if (!props) {
            return;
        }
        const capacityEstimateFromArea = Math.round(props.areaKm2 * 1000);
        const capacity = props.capacityEstimate || capacityEstimateFromArea;
        const count = props.parkingCount || 0;
        const parkingsPerKm2 = count / props.areaKm2;
        const usagePercentage = 100 * count / capacity;
        layer.on('click', (event) => {
            if (this.props.onRegionClicked) {
                this.props.onRegionClicked(region);
            }
        });
        layer.bindTooltip(props.name);
        const text = `
            <h3>${props.name}</h3>
            <b>Pinta-ala</b>:
              ${props.areaKm2.toFixed(2)} km<sup>2</sup><br>
            <b>Arvioitu kapasiteetti</b>:
              ${props.capacityEstimate}<br>
            <b>Arvioitu kapasiteetti (pinta-ala)</b>:
              ${capacityEstimateFromArea}<br>
            <b>Paikkoja per km<sup>2</sup></b>:
              ${props.spotsPerKm2.toFixed(2)}<br>
            <hr>
            <b>Pysäköintejä</b>:
              ${props.parkingCount || 0}<br>
            <b>Pysäköintejä per km<sup>2</sup></b>:
              ${parkingsPerKm2.toFixed(2)}<br>
            <b>Käyttöaste</b>:
              ${usagePercentage.toFixed(2)}&nbsp;%<br>
            `;
        layer.bindPopup(text);
    }

    private handleViewportChange = (viewport: Viewport) => {
        if (!this.map || !this.props.onViewportChanged) {
            return;
        }

        const boundsObj = this.map.leafletElement.getBounds();
        const ne = boundsObj.getNorthEast();
        const sw = boundsObj.getSouthWest();
        const bounds = {
            neLat: ne.lat, neLng: ne.lng,
            swLat: sw.lat, swLng: sw.lng};
        const {center, zoom} = viewport;
        this.props.onViewportChanged({bounds, center, zoom});
    }
}

function getKeyForRegions(regions: Region[]): string {
    if (!regions) {
        return '';
    }
    if (!regions.length) {
        return 'empty';
    }
    let lengthSum = 0;
    let selectedId = '';
    for (let region of regions) {
        if (region.properties) {
            lengthSum += Object.keys(region.properties).length || 0;
            lengthSum += region.properties.parkingCount || 0;
            if (region.properties.isSelected) {
                selectedId = region.id;
            }
        }
    }
    const lastRegion = regions[regions.length - 1];
    return `${regions.length}/${lengthSum}/${lastRegion.id}/${selectedId}`;
}

interface RegionCollection extends
geojson.FeatureCollection<geojson.MultiPolygon, RegionProperties> {
    features: Array<Region>;
}

function getFeatureCollection(regions: Region[]): RegionCollection {
    return {type: 'FeatureCollection', features: regions};
}

function getStyleForRegion(region: Region) {
    const props = region.properties;
    const isSelected = (props && props.isSelected);
    const borderWeight = (isSelected) ? 3 : 1;
    const borderColor = (isSelected) ? '#0000ff' : '#000000';
    const borderOpacity = (isSelected) ? 0.8 : 0.6;
    const fillColor = getColorForRegion(props);
    const fillOpacity = getOpacityForRegion(props);
    return {
        dashArray: (isSelected) ? undefined : '3',
        weight: borderWeight,
        color: borderColor,
        opacity: borderOpacity,
        fillColor: fillColor,
        fillOpacity: fillOpacity,
    };
}

function getColorForRegion(props?: RegionProperties|null): string|undefined {
    const usage = getUsageFactorForRegion(props);
    return (usage != null) ? getColorFromGreenToRed(usage) : undefined;
}

function getOpacityForRegion(props?: RegionProperties|null): number {
    const usageFactor = getUsageFactorForRegion(props);
    if (usageFactor == null) {
        return 0;
    }
    const usageFactor0To1 = Math.min(Math.max(usageFactor, 0), 1);
    return 0.25 + (usageFactor0To1 / 2);
}

function getUsageFactorForRegion(
    props?: RegionProperties|null
): number|undefined {
    if (!props || !props.parkingCount || !props.areaKm2) {
        return undefined;
    }

    const parkingsPerKm2 = props.parkingCount / props.areaKm2;
    return parkingsPerKm2 / 100.0;
}

function getColorFromGreenToRed(ratio: number): string {
    const truncated = Math.min(Math.max(ratio, 0), 1);
    return chroma.scale(['#6d1', '#c21'])(truncated).hex();
}
