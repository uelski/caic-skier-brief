import { useState } from 'react';
import type { Forecast } from '../../../types';
import { getSamples, getLatest } from '../../../api';

export function useForecastSampleList() {
    const [forecasts, setForecasts] = useState<Forecast[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const handleSubmit = async (limit: number) => {
        try {
            setLoading(true);
            const response = await getSamples(limit);
            setForecasts(response);     
        } catch (error) {
            console.error(error);
            setForecasts([]);
        } finally {
            setLoading(false);
        }
    }
    const handleLatest = async () => {
        try {
            setLoading(true);
            const forecast = await getLatest();
            setForecasts([forecast]);
        } catch (error) {
            console.error(error);
            setForecasts([]);
        } finally {
            setLoading(false);
        }
    }
    return { forecasts, handleSubmit, handleLatest, loading };
}