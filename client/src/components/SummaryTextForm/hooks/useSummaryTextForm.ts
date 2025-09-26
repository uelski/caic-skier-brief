import { useState } from 'react';
import type { Forecast, DangerLevel, ElevBand } from '../../../types';
import { predictText } from '../../../api';

export function useSummaryTextForm(reset: () => void) {
    const [forecast, setForecast] = useState<Forecast | null>(null);
    const [summary, setSummary] = useState<string | null>(null);
    const handleSubmit = async (summaryText: string) => {
        try {
            const forecast = await predictText(summaryText);
            console.log(forecast);
            setForecast({
                ...forecast,
                levels: forecast.levels as Record<ElevBand, DangerLevel>
            });
            setSummary(summaryText);
            reset();
        } catch (error: unknown) {
            console.error(error);
            setForecast(null);
        }
    }

    return {
        handleSubmit,
        forecast,
        summary
    }
}