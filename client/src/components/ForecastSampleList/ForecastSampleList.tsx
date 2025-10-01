import { Box, Title, NumberInput, Button } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useForecastSampleList } from './hooks/useForecastSampleList';
import { ForecastSample } from "../ForecastSample/ForecastSample";
export function ForecastSampleList() {
    const form = useForm({
        initialValues: {
            limit: 1,
        },
    });
    const { forecasts, handleSubmit, handleLatest } = useForecastSampleList();
    return (
        <Box>
            <Title c="white">Forecast Samples</Title>
            <form onSubmit={form.onSubmit((values) => handleSubmit(values.limit))}>
                <NumberInput c="white" label="Limit" {...form.getInputProps('limit')} />
                <Button variant="filled" color='myColor.5' type="submit">Submit</Button>
            </form>
                <Button onClick={handleLatest} variant="filled" color='myColor.5' type="submit">Latest</Button>
            {forecasts.map((forecast) => (
                <ForecastSample key={forecast.summary} forecast={forecast} />
            ))}
        </Box>
    );
}