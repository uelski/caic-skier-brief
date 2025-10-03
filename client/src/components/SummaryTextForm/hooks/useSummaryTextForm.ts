import { useEffect, useState } from 'react';
import type { Prediction } from '../../../types';
import { predictText, getModels } from '../../../api';

export function useSummaryTextForm(reset: () => void) {
    const [forecast, setForecast] = useState<Prediction | null>(null);
    const [summary, setSummary] = useState<string | null>(null);
    const [models, setModels] = useState<string[]>([]);
    useEffect(() => {
        const getNewModels = async () => {
            const newModels: any = await getModels();
            setModels(newModels.models);
        }
        getNewModels();
    }, []);
    const handleSubmit = async (summaryText: string, model: string) => {
        try {
            const forecast: Prediction = await predictText(summaryText, model);
            console.log(forecast);
            setForecast(forecast);
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
        summary,
        models
    }
}