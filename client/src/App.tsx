import '@mantine/core/styles.css';

import { SummaryTextForm, ForecastSampleList, Warning, NavLinks } from './components';
import { Box, Container, MantineProvider, Title, createTheme, type MantineColorsTuple, AppShell, Group, Flex, Text } from '@mantine/core';

const myColor: MantineColorsTuple = [
  '#f1f4fe',
  '#e4e6ed',
  '#c8cad3',
  '#a9adb9',
  '#9094a3',
  '#7f8496',
  '#777c91',
  '#63687c',
  '#595e72',
  '#4a5167'
];

const theme = createTheme({
  colors: {
    myColor,
  },
});

function App() {

  return (
    <MantineProvider theme={theme}>
      <Box bg="black" mih="100dvh" w="100%">
        <AppShell
        header={{ height: 60 }}
        padding="md"
        >
          <AppShell.Header withBorder={true} style={{ borderColor: theme!.colors!.myColor![4] }} >
          <Flex bg="black" c="white" h="100%" justify="space-between">
              <Group bg="black" c="white" h="100%" px="md">
                <Text fw={700}>CAIC DATA PROJECT</Text>
              </Group>
              <NavLinks />
            </Flex>
          </AppShell.Header>
          <AppShell.Main>
            <Container p="lg">
              <Warning />
              <Title c="white" ta="center">Avalanche Forecast and Danger Prediction</Title>

              <SummaryTextForm />
              <ForecastSampleList />
            </Container>

          </AppShell.Main>
        </AppShell>
      </Box>

    </MantineProvider>
  )
}

export default App
