import { Box, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import type { Forecast, Prediction } from "../../types";
import { DangerLevels } from "../DangerLevels/DangerLevels";
import { LevelTable } from "../LevelTable/LevelTable";

export function ForecastSample({ forecast }: { forecast: Forecast }) {
    const [prediction, setPrediction] = useState<Prediction>({} as Prediction);

    useEffect(() => {
        const newPrediction: Prediction = {
            above_treeline: forecast.levels.above_treeline,
            below_treeline: forecast.levels.below_treeline,
            treeline: forecast.levels.treeline,
        };
        setPrediction(newPrediction);
    }, [forecast]);

    return (
        <Box>
            <Title fz="lg" c="white">Summary</Title>
            <Text c="white">{forecast.summary}</Text>
            <DangerLevels levels={forecast.levels} />
            <LevelTable prediction={prediction} />
        </Box>
    );
}