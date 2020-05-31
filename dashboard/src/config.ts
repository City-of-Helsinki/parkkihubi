import { Point } from './components/types';

export const isDev: boolean = (process.env.NODE_ENV === 'development');

export const apiBaseUrl: string = process.env.REACT_APP_API_URL || (
    (isDev)
        ? 'http://localhost:8000/'
        : 'https://api.parkkiopas.fi/');

let mapPoint: Point;
if (typeof process.env.REACT_APP_API_CENTER !== 'undefined') {
    const envPoint = process.env.REACT_APP_API_CENTER!.split(',').map(Number);
    mapPoint = [envPoint[0], envPoint[1]];
} else {
    mapPoint = [60.17, 24.94]; // Default to Helsinki centrum
}
export const centerCoordinates: Point = mapPoint;
