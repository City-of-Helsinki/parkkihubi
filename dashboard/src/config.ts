import { Point } from './components/types';

export const isDev: boolean = import.meta.env.DEV;
export const isProd: boolean = import.meta.env.PROD;

export const apiBaseUrl: string = import.meta.env.VITE_API_URL || (
    (isDev)
        ? 'http://localhost:8000/'
        : 'https://api.parkkiopas.fi/');

let mapPoint: Point;
if (typeof import.meta.env.VITE_MAP_CENTER_COORDS !== 'undefined') {
    const envPoint = import.meta.env.VITE_MAP_CENTER_COORDS.split(',').map(Number);
    mapPoint = [envPoint[0], envPoint[1]];
} else {
    mapPoint = [60.17, 24.94]; // Default to Helsinki centrum
}
export const centerCoordinates: Point = mapPoint;
