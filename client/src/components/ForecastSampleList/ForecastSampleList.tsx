import { Box, Title, NumberInput, Button, Text, Loader } from "@mantine/core";
import { useForm } from '@mantine/form';
import { useForecastSampleList } from './hooks/useForecastSampleList';
import { LevelTable } from "../LevelTable/LevelTable";

export function ForecastSampleList() {
    const form = useForm({
        initialValues: {
            limit: 1,
        },
    });
    const { forecasts, handleSubmit, handleLatest, loading } = useForecastSampleList();
    return (
        <Box mt="lg">
            <Title mb="sm" mt="md" fz="xl" c="white">Forecast Samples</Title>
            <form onSubmit={form.onSubmit((values) => handleSubmit(values.limit))}>
                <NumberInput c="white" label="Limit" {...form.getInputProps('limit')} />
                <Button variant="outline" color='myColor.2' type="submit">Submit</Button>
                <Button m="md" onClick={handleLatest} variant="outline" color='myColor.2' type="submit">Latest</Button>
            </form>
            {loading && <Loader color="white" />}            
            {forecasts.map((forecast) => (
                <Box>
                    <Title fz="lg" c="white" mb="sm">Summary</Title>
                    <Text mb="sm" c="white">{forecast.summary}</Text>
                    <LevelTable prediction={{
                        above_treeline: forecast.levels.above_treeline,
                        below_treeline: forecast.levels.below_treeline,
                        treeline: forecast.levels.treeline,
                    }} />
                </Box>
            ))}
        </Box>
    );
}