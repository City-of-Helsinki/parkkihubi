declare module 'react-datetime/src/CalendarContainer' {
    import * as React from 'react';

    interface Props {
        view: string;  // 'years'|'months'|'days'|'time';
        viewProps: any;
        onClickOutside: () => void;
    }

    export default class CalendarContainer extends React.Component<Props> {
    }
}
