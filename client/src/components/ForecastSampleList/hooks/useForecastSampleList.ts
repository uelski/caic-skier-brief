import { useState } from 'react';
import type { Forecast } from '../../../types';
import { getSamples, getLatest } from '../../../api';

export function useForecastSampleList() {
    const [forecasts, setForecasts] = useState<Forecast[]>([]);
    const handleSubmit = async (limit: number) => {
        try {
            const response = await getSamples(limit);
            setForecasts(response);     
        } catch (error) {
            console.error(error);
            setForecasts([]);
        }
    }
    const handleLatest = async () => {
        try {
            const forecast = await getLatest();
            setForecasts([forecast]);
        } catch (error) {
            console.error(error);
            setForecasts([]);
        }
    }
    return { forecasts, handleSubmit, handleLatest };
}